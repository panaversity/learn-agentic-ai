import streamlit as st
st.title("Text Display")
st.write("Write content")
st.text("Text content...")
st.markdown("# Markdown content")
st.latex(r''' e^{i\pi} + 1 = 0 ''')
st.title("Title content")
st.header("Header content")
st.subheader("Sub header content")
st.code("[i for i in range(1,10)]")

st.title("Data Display")

import pandas as pd

df : pd.DataFrame = pd.DataFrame({"Col1":[1,2,3],
                                "Col2":['a','b','c']})

# st.write(df)
# st.table(df)
# st.json(df.to_dict())
# st.metric('My metric', 42, 2)

st.title("Display Media")
st.video("https://youtu.be/_OVnXw2ldog?si=2qsVAd3WdTUAlRVH")
st.image("data:image/png;base64,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")
st.audio("urdu.mp3")