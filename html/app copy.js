// --- State ---
let eraWords = [];
let repDict = new Map();
// 既存コードの先頭付近に追記
let settings = null;

// 起動時に settings.json を読み込む
async function loadSettings() {
  try {
    const res = await fetch('settings.json', { cache: 'no-store' });
    if (!res.ok) throw new Error('settings.json を取得できませんでした');
    settings = await res.json();
  } catch (e) {
    console.warn(e);
    showToast('設定ファイルの読み込みに失敗（手動選択に切替）', false);
  }
}

// Excel からルール読込（settings.rules.excelUrl を利用）
async function loadRulesFromExcel() {
  if (!settings?.rules?.excelUrl) {
    showToast('settings.json に excelUrl が未設定です', false);
    return false;
  }
  try {
    const res = await fetch(settings.rules.excelUrl, { cache: 'no-store' });
    if (!res.ok) throw new Error('Excel を取得できませんでした');
    const ab = await res.arrayBuffer();

    // Excel をパース
    const wb = XLSX.read(ab, { type: 'array' });

    // del シート
    const delSheetName = settings.rules.sheets?.del || 'del';
    const delSheet = wb.Sheets[delSheetName];
    if (!delSheet) throw new Error(`シート '${delSheetName}' が見つかりません`);
    const delJson = XLSX.utils.sheet_to_json(delSheet, { header: 1, blankrows: false });
    // 1行目はヘッダ想定：2行目以降のA列
    eraWords = delJson.slice(1).map(r => (r?.[0] ?? '').toString().trim()).filter(Boolean);

    // replace シート
    const repSheetName = settings.rules.sheets?.replace || 'replace';
    const repSheet = wb.Sheets[repSheetName];
    if (!repSheet) throw new Error(`シート '${repSheetName}' が見つかりません`);
    const repJson = XLSX.utils.sheet_to_json(repSheet, { header: 1, blankrows: false });
    repDict = new Map();
    repJson.slice(1).forEach(r => {
      const k = (r?.[0] ?? '').toString().trim();
      const v = (r?.[1] ?? '').toString().trim();
      if (k) repDict.set(k, v);
    });

    $('#ruleStatus').textContent = `読込済み: del=${eraWords.length}件, replace=${repDict.size}件（Excel）`;
    showToast('Excel からルールを読み込みました。');
    return true;
  } catch (e) {
    console.error(e);
    showToast(`Excel 読込に失敗: ${e.message}`, false);
    return false;
  }
}

// 既存の loadRules() は手動CSV読込用として残す
// ↓↓↓ 既存の loadRules() はそのまま ↓↓↓

// 起動時：settings を読んで自動ロードを試行
(async () => {
  await loadSettings();
  if (settings?.rules?.excelUrl) {
    // 自動読込に成功したら UI を更新、失敗時は手動CSVにフォールバック
    const ok = await loadRulesFromExcel();
    if (!ok) {
      // 失敗した場合でも手動で del.csv/replace.csv を選択して「ルール読込」できます
    }
  }
})();

// 「ルール読込」ボタンは優先度：Excel設定→手動CSV
$('#loadBtn').addEventListener('click', async () => {
  if (settings?.rules?.excelUrl) {
    const ok = await loadRulesFromExcel();
    if (ok) return;
  }
  // Excel設定が無い/失敗した場合は手動CSV
  await loadRules();
});

// 以降（変換実行など）は既存のハンドラのままでOK

// --- Utils ---
const $ = (sel) => document.querySelector(sel);
const showToast = (msg, ok = true) => {
  const t = document.createElement('div');
  t.textContent = msg;
  t.className = ok ? '' : 'err';
  $('#toast').appendChild(t);
  setTimeout(() => t.remove(), 2400);
};

function parseCSV(text) {
  // シンプルCSVパーサ（カンマ区切り・ダブルクォート対応）
  const rows = [];
  let i = 0, cell = '', row = [], inQuotes = false;
  while (i < text.length) {
    const ch = text[i];
    if (inQuotes) {
      if (ch === '"' && text[i + 1] === '"') { cell += '"'; i += 2; continue; }
      if (ch === '"') { inQuotes = false; i++; continue; }
      cell += ch; i++; continue;
    }
    if (ch === '"') { inQuotes = true; i++; continue; }
    if (ch === ',') { row.push(cell); cell = ''; i++; continue; }
    if (ch === '\n' || ch === '\r') {
      if (cell.length || row.length) { row.push(cell); rows.push(row); row = []; cell = ''; }
      if (ch === '\r' && text[i + 1] === '\n') i++;
      i++; continue;
    }
    cell += ch; i++;
  }
  if (cell.length || row.length) { row.push(cell); rows.push(row); }
  return rows;
}

function readFileAsText(file) {
  return new Promise((resolve, reject) => {
    const fr = new FileReader();
    fr.onerror = () => reject(fr.error);
    fr.onload = () => resolve(fr.result);
    fr.readAsText(file, 'utf-8');
  });
}

// --- Load Rules (equivalent to load_rules) ---
async function loadRules() {
  const delFile = $('#delFile').files[0];
  const repFile = $('#repFile').files[0];
  if (!delFile || !repFile) {
    showToast('del.csv / replace.csv を選択してください。', false);
    return false;
  }
  try {
    const [delText, repText] = await Promise.all([
      readFileAsText(delFile), readFileAsText(repFile)
    ]);
    // del.csv
    const delRows = parseCSV(delText);
    eraWords = delRows.slice(1)
      .filter(r => r && r[0] !== undefined)
      .map(r => (r[0] || '').trim())
      .filter(Boolean);

    // replace.csv
    const repRows = parseCSV(repText);
    repDict = new Map();
    repRows.slice(1).forEach(r => {
      if (!r || r.length < 2) return;
      const k = (r[0] || '').trim();
      const v = (r[1] || '').trim();
      if (k) repDict.set(k, v);
    });

    $('#ruleStatus').textContent = `読込済み: del=${eraWords.length}件, replace=${repDict.size}件`;
    showToast('ルールを読み込みました。');
    return true;
  } catch (e) {
    console.error(e);
    showToast('ルール読込に失敗しました。', false);
    return false;
  }
}

// --- Core Logic (ported from Python) ---
function abbreviation(words, formatStyle) {
  let wordsList = words.split(/\s+/);
  wordsList = wordsList.map(w => {
    const comma = w.includes(',') ? ',' : '';
    const cleaned = w.replace(',', '');
    if (eraWords.includes(cleaned)) {
      return '';
    } else if (repDict.has(cleaned)) {
      return repDict.get(cleaned) + '.' + comma;
    }
    return w;
  });
  let result = wordsList.filter(Boolean).join(' ');

  if (formatStyle === 'tex') {
    result = result.replace(/(pp\. )(\d+)-(\d+)/g, '$1$2--$3');
  }
  result = result.replace(/,$/, '.');
  if (!result.endsWith('.')) result += '.';

  if (formatStyle === 'tex') {
    result = '\\textit{' + result;
    // 最初のカンマの直前で閉じる（Python版の置換を再現）
    result = result.replace(',', '},', 1);
  }
  return result;
}

function search(pattern, text) {
  const m = text.match(pattern);
  return m ? m[1].trim() : null;
}

function formatReference(originalText, formatStyle) {
  // doi以降を削除（大文字小文字無視）
  let text = originalText.replace(/doi:.*/i, '');
  text = text.replace(/\n.*/, '').trim();

  const name = search(/(.*?),\s*\\"/, text) ?? search(/(.*?),\s*\"/, text);
  const title = search(/\\"(.*?)\\"/, text) ?? search(/\"(.*?)\"/, text);
  const journalInfo = search(/,\\"\s*(.*?)$/, text) ?? search(/,\"\s*(.*?)$/, text);

  if (!(name && title && journalInfo)) {
    return "入力形式が正しくない可能性があります。\n'著者名, \"タイトル\" ジャーナル情報' の形式か確認してください。";
  }

  let nameRep = name.replace(' and', ', and');
  if (formatStyle === 'tex') {
    nameRep = nameRep.replace(/et al/g, '\\textit{et al}');
  }
  const journalInfoAbb = abbreviation(journalInfo, formatStyle);

  let finalText = text.replace(name, nameRep);
  if (formatStyle === 'tex') {
    finalText = finalText.replace(`"${title}"`, `\`\`${title}''`);
  }
  finalText = finalText.replace(journalInfo, journalInfoAbb);
  return finalText;
}

async function copyToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text);
    showToast('クリップボードにコピーしました。');
  } catch (e) {
    // フォールバック（選択→execCommand）
    const ta = document.createElement('textarea');
    ta.value = text;
    document.body.appendChild(ta);
    ta.select();
    try {
      document.execCommand('copy');
      showToast('クリップボードにコピーしました。');
    } catch {
      showToast('自動コピーに失敗しました。手動でコピーしてください。', false);
    } finally {
      document.body.removeChild(ta);
    }
  }
}

// --- Wire UI ---
$('#loadBtn').addEventListener('click', loadRules);

$('#run').addEventListener('click', async () => {
  const ok = (eraWords.length || repDict.size) ? true : await loadRules();
  if (!ok) return;
  const inputVal = $('#in').value.trim();
  if (!inputVal) { showToast('入力が空です。', false); return; }
  const fmt = document.querySelector('input[name="fmt"]:checked').value;
  const result = formatReference(inputVal, fmt);
  $('#out').value = result;
  await copyToClipboard(result);
});

$('#clear').addEventListener('click', () => { $('#in').value = ''; $('#out').value = ''; });
$('#copy').addEventListener('click', async () => {
  const t = $('#out').value;
  if (!t) { showToast('出力が空です。', false); return; }
  await copyToClipboard(t);
});

// Keyboard shortcut: Ctrl/Cmd + Enter
document.addEventListener('keydown', (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
    e.preventDefault();
    $('#run').click();
  }
});
