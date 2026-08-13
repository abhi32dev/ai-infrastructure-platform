"""
Query Transformation, Rewriting & HyDE (Hypothetical Document Embeddings) Engine.
Implements 3 query optimization strategies:
1. HyDE: Generates hypothetical answer embeddings to bridge query-document semantic gap.
2. Sub-Query Decomposition: Decomposes complex queries into sub-queries.
3. Query Rewriting & Acronym Expansion: Enhances raw query vocabulary for dense/sparse retrieval.
"""

from typing import List


class QueryTransformer:
    def __init__(self):
        # Acronym & Domain Term Dictionary
        self.domain_expansions = {
            "sla": "Service Level Agreement 99.999% availability uptime",
            "rag": "Retrieval Augmented Generation vector retrieval embeddings",
            "nlb": "Network Load Balancer Amazon EC2 multi-AZ fault tolerance",
            "alb": "Application Load Balancer cross-AZ health check target routing",
            "sftp": "Secure File Transfer Protocol SSH manifest collector",
            "mcp": "Model Context Protocol tool execution permission gates",
            "hitl": "Human in the loop approval sensitive operation"
        }

    def rewrite_query(self, query: str) -> str:
        """
        Rewrites query by expanding technical domain acronyms and normalizing terms.
        """
        words = query.lower().split()
        expanded_words = []
        for w in words:
            clean_w = w.strip("?,.!")
            if clean_w in self.domain_expansions:
                expanded_words.append(self.domain_expansions[clean_w])
            else:
                expanded_words.append(w)
        return " ".join(expanded_words)

    def generate_hypothetical_document(self, query: str) -> str:
        """
        HyDE (Hypothetical Document Embedding):
        Generates a synthetic ideal response chunk for embedding vector search.
        """
        rewritten = self.rewrite_query(query)
        hypothetical_answer = (
            f"Regarding {rewritten}: The system architecture implements high availability, "
            f"fault isolation, and durable state handling. Specific configurations specify "
            f"operational parameters, threshold metrics, and step-by-step procedures to maintain SLA."
        )
        return hypothetical_answer

    def decompose_query(self, query: str) -> List[str]:
        """
        Decomposes complex multi-part questions into individual sub-queries.
        """
        if "and" in query.lower() or "compare" in query.lower() or "also" in query.lower():
            # Split heuristic on conjunctions or clauses
            parts = [p.strip() for p in query.replace("also", "and").split("and") if p.strip()]
            if len(parts) > 1:
                return parts
        return [query]
