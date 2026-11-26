import type { HarakahInfo, Letter, Phase } from "../types";

export const HARAKAT: HarakahInfo[] = [
  { id: "fatha", mark: "َ", name: "فَتْحَة", sound: "اَ" },
  { id: "damma", mark: "ُ", name: "ضَمَّة", sound: "اُ" },
  { id: "kasra", mark: "ِ", name: "كَسْرَة", sound: "اِ" },
];

export function harakahById(id: string): HarakahInfo {
  const h = HARAKAT.find((x) => x.id === id);
  if (!h) throw new Error(`unknown harakah: ${id}`);
  return h;
}

/** Returns the letter glyph with the harakah mark applied, e.g. "بَ". */
export function applyHarakah(letter: Letter, h: HarakahInfo): string {
  return letter.char + h.mark;
}

/**
 * The 28 letters of the Arabic alphabet in the traditional order used by the
 * Qaida Nooraniyah. `hard` flags the emphatic/pharyngeal letters that children
 * raised in non-Arabic environments most often confuse.
 */
export const LETTERS: Letter[] = [
  { id: "alif", char: "ا", name: "ألِف" },
  { id: "ba", char: "ب", name: "باء" },
  { id: "ta", char: "ت", name: "تاء" },
  { id: "tha", char: "ث", name: "ثاء", hard: true, tip: "طرف اللسان بين الأسنان مع نَفَس (مثل th في الإنجليزية)." },
  { id: "jim", char: "ج", name: "جيم" },
  { id: "ha2", char: "ح", name: "حاء", hard: true, tip: "من وسط الحلق، صوت مهموس بلا حشرجة (ليست هاء ولا خاء)." },
  { id: "kha", char: "خ", name: "خاء", hard: true, tip: "من أعلى الحلق مع حكّة خفيفة." },
  { id: "dal", char: "د", name: "دال" },
  { id: "dhal", char: "ذ", name: "ذال", hard: true, tip: "طرف اللسان بين الأسنان مع جهر (مثل th في this)." },
  { id: "ra", char: "ر", name: "راء", tip: "تكرار خفيف لطرف اللسان." },
  { id: "zay", char: "ز", name: "زاي" },
  { id: "sin", char: "س", name: "سين" },
  { id: "shin", char: "ش", name: "شين" },
  { id: "sad", char: "ص", name: "صاد", hard: true, tip: "سين مُفخَّمة: ارفع مؤخرة اللسان نحو الحنك." },
  { id: "dad", char: "ض", name: "ضاد", hard: true, tip: "حافة اللسان على الأضراس العليا، صوت مُطبَق (حرف العربية المميّز)." },
  { id: "ta2", char: "ط", name: "طاء", hard: true, tip: "تاء مُفخَّمة قوية مع إطباق اللسان على الحنك." },
  { id: "za2", char: "ظ", name: "ظاء", hard: true, tip: "ذال مُفخَّمة: طرف اللسان بين الأسنان مع تفخيم." },
  { id: "ayn", char: "ع", name: "عَين", hard: true, tip: "من وسط الحلق بضغط، أعمق من الهمزة." },
  { id: "ghayn", char: "غ", name: "غَين", hard: true, tip: "من أعلى الحلق، كالغرغرة الخفيفة." },
  { id: "fa", char: "ف", name: "فاء" },
  { id: "qaf", char: "ق", name: "قاف", hard: true, tip: "من أقصى اللسان عند اللهاة، أعمق من الكاف." },
  { id: "kaf", char: "ك", name: "كاف" },
  { id: "lam", char: "ل", name: "لام" },
  { id: "mim", char: "م", name: "ميم" },
  { id: "nun", char: "ن", name: "نون" },
  { id: "ha", char: "ه", name: "هاء" },
  { id: "waw", char: "و", name: "واو" },
  { id: "ya", char: "ي", name: "ياء" },
];

export function letterById(id: string): Letter {
  const l = LETTERS.find((x) => x.id === id);
  if (!l) throw new Error(`unknown letter: ${id}`);
  return l;
}

export const PHASES: Phase[] = [
  {
    id: "letters",
    title: "الحروف",
    subtitle: "نطق الحروف مفردة بالحركات الثلاث",
    available: true,
  },
  {
    id: "qaida",
    title: "القاعدة النورانية",
    subtitle: "الحروف المركّبة والمدود والتنوين",
    available: false,
  },
  {
    id: "quran",
    title: "القرآن والتجويد",
    subtitle: "التلاوة والتحفيظ وأحكام التجويد",
    available: false,
  },
];
