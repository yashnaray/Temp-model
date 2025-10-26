from knowledge_base import KnowledgeBase

kb = KnowledgeBase("./knowledge_base")
kb.load_knowledge_base()

print("Doc counts by category:")
for k, v in kb.documents.items():
    print(f"  {k}: {len(v)}")

# Peek at first insurance doc
docs = kb.get_documents_by_category("insurance_guidelines")
if docs:
    print("\nPreview (first 500 chars):\n")
    print(docs[0].page_content[:500])