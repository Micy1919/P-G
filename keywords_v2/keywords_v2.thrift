namespace cpp ultrain.nlp

struct News {
  1: string nid,
  2: string main_content,
  3: string title,
  4: string url
}

struct Keyword {
  1: string term,
  2: double score
}

struct FindKeywordsResponse {
  1: list<Keyword> keywords
}

struct FindKeywordsRequest {
  1: News news,
  2: i32 topK
}

service SupervisedKeyword {
  FindKeywordsResponse find_keywords(1:FindKeywordsRequest request)
}
