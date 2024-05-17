trip_query = """
match (n:Place)
where
n.category in ["food", "recreation", "entertainment", "shopping"]
return n
"""
