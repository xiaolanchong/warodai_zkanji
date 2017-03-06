# Script to convert Warodai RU-JP dictionary (warodai.ru) to ZKanji (http://zkanji.sourceforge.net/) app import format

Format description is at
https://web.archive.org/web/20130712024620/http://zkanji.wordpress.com/2013/02/14/planned-exportimport-file-format/

## Problems with conversion:
- Roman numbers in words: ああI (а:)〔1-001-1-03〕
- Html formatting tags in definitions: 1) <i>межд.</i> ах!;
- Multiple word notation:
    1-to-1: あばずれ, あばずれおんな【阿婆擦れ, 阿婆擦れ女】
    1-to-many: あばれまわる【暴れ回る･暴れ廻る】
- Kanji which are not in ZKanji known list, thus skipped: 蝱 (zkanji bug)
- Too long definitions (~700 symbols) break importing completely (zkanji bug)
- Nonsense cyrillic text displaying even in UTF8 encoding, no font change helps (zkanji bug)
