
namespace cpp ultrain.nlp

struct News {
  1: string nid,
  2: string main_content,
  3: string title,
  4: string url,
  5: list<string> meta_keywords
}

struct Keyword {
  1: string term,
  2: double weight,
  3: string origin_format,
  4: double origin_score
}

struct Entity {
  1: string stem_format,
  2: double weight,
  3: string origin_format,
  4: double origin_score
}

struct KeywordResult {
  1: list<Keyword> full_keywords,
  2: list<Keyword> title_keywords,
  3: list<Entity> relevant_entities,
  4: list<Entity> quality_entities
}

struct KeywordTimeSeries {
  1: string orig_keyword,
  2: string stem_keyword,
  3: map<string, i32> timeseries
}

enum WordnetType {
  WORDNET_KEYWORD = 0,
  WORDNET_TITLE_KEYWORD = 1,
  WORDNET_ENTITY = 2,
}

struct WordnetReq {
  1: WordnetType type,
  2: string main_content,
  3: list<Keyword> typed_keywords,
}

struct WordnetKeywordResult {
  1: list<Keyword> wordnet_keywords,
}

service FindKeywords {
  bool index_news(1:News news),
  list<Keyword> news_keywords(1:string news_nid, 2:i32 topK),
  list<Keyword> index_and_keywords(1:News news, 2:i32 topK),
  KeywordResult find_keywords(1:News news, 2:i32 topK),
  list<string> simple_words(1:News news, 2:i32 topK),
  void delete_news(1:string news_nid),
  KeywordTimeSeries timeseries(1:string orig_keyword),
  WordnetKeywordResult search_wordnet(1:WordnetReq req)
}