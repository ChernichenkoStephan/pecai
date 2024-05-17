doc_embeddings_query = """
CALL db.index.vector.queryNodes('doc_embeddings', $limit, $embeddings) 
YIELD node, score
MATCH (node)
WHERE score > $score_threshold
RETURN 
    node
ORDER BY score DESC 
"""

span_embeddings_query = """
CALL db.index.vector.queryNodes('span_embeddings', $limit, $embeddings) 
YIELD node, score
MATCH (node)
WHERE score > $score_threshold
RETURN 
    node
ORDER BY score DESC 
"""

place_embeddings_query = """
CALL db.index.vector.queryNodes('place_embeddings', $limit, $embeddings) 
YIELD node, score
MATCH (node)
WHERE score > $score_threshold
RETURN 
    node
ORDER BY score DESC 
"""
