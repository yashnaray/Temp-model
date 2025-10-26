import streamlit as st
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import PropertyAnalysisApp

st.set_page_config(page_title="Property Analysis System", layout="wide")

@st.cache_resource
def load_app():
    return PropertyAnalysisApp()

def main():
    st.title("🏠 Property Analysis System")
    
    app = load_app()
    
    # Sidebar for setup
    with st.sidebar:
        st.header("Setup")
        location = st.text_input("Location for data scraping:")
        
        if st.button("Initialize Knowledge Base"):
            with st.spinner("Setting up knowledge base..."):
                app.setup_knowledge_base(location if location else None)
            st.success("Knowledge base initialized!")
    
    # Main interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("Ask a Question")
        question = st.text_area("Enter your property-related question:")
        
        query_type = st.selectbox(
            "Query Type:",
            ["general", "cost_estimation", "regulatory"]
        )
        
        if st.button("Get Answer") and question:
            with st.spinner("Processing..."):
                try:
                    result = app.query_property(question, query_type)
                    
                    st.subheader("Answer:")
                    st.write(result['answer'])
                    
                    st.subheader("Enhanced Question:")
                    st.write(result['enhanced_question'])
                    
                    st.subheader("Sources:")
                    st.write(f"Found {len(result['source_documents'])} relevant documents")
                    
                except Exception as e:
                    st.error(f"Error: {e}")
    
    with col2:
        st.header("System Info")
        if hasattr(app, 'vector_store') and app.vector_store.vector_store:
            stats = app.vector_store.get_stats()
            st.metric("Total Documents", stats['total_documents'])
            st.write("Categories:", stats['categories'])

if __name__ == "__main__":
    main()