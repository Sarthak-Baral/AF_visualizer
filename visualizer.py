import streamlit as st
import streamlit.components.v1
import networkx as nx
from pyvis.network import Network
from dungs_AF_solver import read_tgf_file, run_mu_toksia, highlight_nodes

    

# Define the streamlit app
def main():
    st.title('Dung\'s Argumentation Framework Visualization')

    # Define the widgets for the web application
    st.sidebar.header("File Upload")
    uploaded_file = st.sidebar.file_uploader("Choose a TGF file")

    if uploaded_file is not None:
        # Check if the uploaded file is not empty
        file_contents = uploaded_file.getvalue()
        if len(file_contents) > 0:
            graph = read_tgf_file(uploaded_file)

            # Create pyvis network and network graph data
            net = Network(height='600px', width='100%', directed=True)
            net.from_nx(graph)
        
            # Show the graph
            net.write_html('graph.html')
            streamlit.components.v1.html(open('graph.html').read(), height=600, width=1000)
            #st.graphviz_chart(nx.drawing.nx_pydot.to_pydot(graph).to_string())

            # Choose computation
            #task = st.selectbox("Select a computation", ["Reachability", "Deadlock Freedom", "Boundedness"])

            reasoning = st.selectbox('Reasoning:', ('DC', 'DS', 'SE'))
            semantics = st.selectbox('Semantics:', ('CO', 'PR', 'ST', 'SST', 'STG', 'ID'))

            # Ask the user for a query if necessary
            if reasoning == 'DC' or reasoning == 'DS':
                query = st.text_input('Enter query:')
            else:
                query = None

            # Enter path to mu-toksia program
            mu_toksia_path = st.text_input("Enter path to mu-toksia program")



            # Run computation
            if st.button("Run Computation"):
                output = run_mu_toksia(reasoning, semantics, uploaded_file.name, "tgf", mu_toksia_path, query)
                st.text_area('Output:', value=output, height=400)
                #highlighted_nodes = highlight_nodes(graph, output.split("\n"))
                #st.graphviz_chart(nx.drawing.nx_pydot.to_pydot(graph, highlighted_nodes).to_string())

        else:
            st.write('File is empty!')
             
    else:
        st.write('Please upload a file.')


if __name__ == "__main__":
    main()

