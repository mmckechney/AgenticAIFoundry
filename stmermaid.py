import streamlit as st

clean_diagram = """
graph TD;
    A[Start] --> B[Process];
    B --> C[End];
"""
mermaid_code = f"""
<div class="mermaid">
    {clean_diagram}
</div>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>
    mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
</script>
"""
st.markdown(mermaid_code, unsafe_allow_html=True)