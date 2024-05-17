doc_hybrid_query = """
CALL db.index.vector.queryNodes('doc_embeddings', $limit, $embeddings) 
YIELD node, score
MATCH (node)-[]-(kw:Keyword)
WHERE 
    score > $score_threshold
    AND kw.text in $keys
RETURN 
    node
ORDER BY score DESC 
"""

span_hybrid_query = """
CALL db.index.vector.queryNodes('span_embeddings', $limit, $embeddings) 
YIELD node, score
MATCH (node)-[]-(kw:Keyword)
WHERE 
    score > $score_threshold
    AND kw.text in $keys
RETURN 
    node
ORDER BY score DESC 
"""
