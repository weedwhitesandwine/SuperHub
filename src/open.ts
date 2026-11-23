/**
 * Open a target from the dashboard, then leave to the OS so it comes to the
 * foreground (a target launched behind the fullscreen plugin view looks dead).
 * The bubble is restored on the way out so the user can return. On failure we
 * stay and show a dialog instead of silently closing.
 *
 * Files (note/pdf/epub/…) prefer the Chauvet SDK opener PluginFileAPI.openFile:
 *  - it HONOURS the page jump (the old Document intent ignored `page` and always
 *    reopened the last-viewed page; the long-standing "viewer ignores the page"
 *    bug), and
 *  - it opens epub/cbz/xps/fb2/note, not only the two hardcoded intent targets.
 * The legacy component intents remain as a fallback for the old firmware / any
 * device where openFile is absent or refuses.
 */
import {NativeModules} from 'react-native';
import {NativeUIUtils, PluginCommAPI, PluginFileAPI} from 'sn-plugin-lib';

import {leavePlugin} from './bubble';

const {DashboardNative} = NativeModules;

async function go(fn: () => Promise<unknown>, what: string): Promise<void> {
  try {
    await fn();
    leavePlugin();
  } catch {
    try {
      await NativeUIUtils.showRattaDialog(`Couldn't ${what}.`, '', 'OK', false);
    } catch {
      /* ignore */
    }
  }
}

/** Open a folder in the file manager. */
export function openFolder(path: string) {
  return go(() => DashboardNative.openFolder(path), 'open the folder');
}

/**
 * Dashboard pages are 1-based (0/undefined = "no specific page, keep last view").
 * PluginFileAPI.openFile is 0-based: a value >= 0 jumps to that page, -1 keeps
 * the last viewed page.
 */
function toZeroBasedPage(page: number): number {
  return page && page > 0 ? page - 1 : -1;
}

/** Try the SDK opener with an ALREADY-RESOLVED page (firmware page space, -1 =
 *  keep last-viewed). Returns true only if the file was actually opened.
 *  Absent method / thrown error / {success:false} → false so we fall back. */
async function openViaSdk(path: string, sdkPage: number): Promise<boolean> {
  const fn = (PluginFileAPI as any)?.openFile;
  if (typeof fn !== 'function') return false;
  try {
    const res: any = await PluginFileAPI.openFile(path, sdkPage);
    if (res === true) return true;
    if (res && typeof res === 'object') {
      if (res.success === false) return false;
      // APIResponse success (or a bare object with no error) → opened.
      return res.success === true || res.error == null;
    }
    return false;
  } catch {
    return false;
  }
}

/** Open a file target: note editor for .note, Document viewer for .pdf/.epub/…
 *  `page` is 1-based (0 = keep last-viewed page). */
export async function openFile(path: string, page = 0): Promise<void> {
  if (await openViaSdk(path, toZeroBasedPage(page))) {
    leavePlugin();
    return;
  }
  // Fallback: legacy component intents (old firmware / openFile unavailable).
  // The Document intent's `page` extra is known to be ignored by the viewer.
  const isDoc = /\.(pdf|epub)$/i.test(path);
  await go(
    () => (isDoc ? DashboardNative.openDocument(path, page) : DashboardNative.openNote(path, page)),
    isDoc ? 'open the document' : 'open the note',
  );
}

/** Open a note at a RAW firmware page (as captured by getCurrentPageNum); no
 *  ±1 conversion, so a clip backlink lands on the exact page it was taken from.
 *  Used only by Note Clips. */
export async function openFileAtPage(path: string, rawPage: number): Promise<void> {
  const p = typeof rawPage === 'number' ? rawPage : -1;
  if (await openViaSdk(path, p)) {
    leavePlugin();
    return;
  }
  const isDoc = /\.(pdf|epub)$/i.test(path);
  await go(
    () => (isDoc ? DashboardNative.openDocument(path, p) : DashboardNative.openNote(path, p)),
    isDoc ? 'open the document' : 'open the note',
  );
}

/** Launch an app by "package/activity"; leaves to the OS. */
export function launchApp(component: string) {
  return go(() => DashboardNative.launchActivity(component), 'launch the app');
}

const pad = (n: number) => String(n).padStart(2, '0');

/** Make a new notebook in `folder`, named the way the Supernote names them
 *  (YYYYMMDD_HHMMSS.note), then open it. Without a template, the plain white page. */
export async function createNote(folder: string, template?: string, recognition?: boolean): Promise<void> {
  const d = new Date();
  const name = `${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}_${pad(d.getHours())}${pad(d.getMinutes())}${pad(d.getSeconds())}`;
  const notePath = `${folder.replace(/\/$/, '')}/${name}.note`;
  try {
    let tpl = template;
    if (!tpl) {
      const r: any = await PluginCommAPI.getNoteSystemTemplates();
      const list: any[] = (r?.success ? r.result : r) ?? [];
      tpl = (list.find(t => /white/i.test(t?.name ?? '')) ?? list[0])?.name;
    }
    const res: any = await PluginFileAPI.createNote({notePath, template: tpl ?? 'style_white', mode: recognition ? 1 : 0, isPortrait: true});
    if (!(res === true || res?.success)) throw new Error(res?.error?.message ?? 'createNote refused');
  } catch {
    try {
      await NativeUIUtils.showRattaDialog("Couldn't make a new note.", '', 'OK', false);
    } catch {
      /* ignore */
    }
    return;
  }
  await openFile(notePath, 1);
}

/** Make a new typed document (YYYYMMDD_HHMMSS.doc) in `folder` and open it in the
 *  Supernote's document editor, like the Files app's new-document button. */
export async function createDoc(folder: string): Promise<void> {
  const d = new Date();
  const name = `${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}_${pad(d.getHours())}${pad(d.getMinutes())}${pad(d.getSeconds())}`;
  await go(() => DashboardNative.newTypedDocument(`${folder.replace(/\/$/, '')}/${name}.doc`), 'make a new document');
}

/** The Supernote's own page styles, for the New note button's settings. */
export async function systemTemplates(): Promise<string[]> {
  try {
    const r: any = await PluginCommAPI.getNoteSystemTemplates();
    const list: any[] = (r?.success ? r.result : r) ?? [];
    return list.map(t => String(t?.name ?? '')).filter(Boolean);
  } catch {
    return [];
  }
}
