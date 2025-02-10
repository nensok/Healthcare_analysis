import streamlit as st
import pandas as pd
import plotly.express as px

import os


skyblue = "#0CAFFF"

# Load the dataset
@st.cache_data
def load_data():
    df = pd.read_excel(r"data/healthcare_data.xlsx", engine="openpyxl", dtype=str, parse_dates=["Admission_Date", "Discharge_Date"])
    df["Admission_Month"] = df["Admission_Date"].dt.strftime("%Y-%m")  # Extract month-year
    df["Discharge_Month"] = df["Discharge_Date"].dt.strftime("%Y-%m")  # Extract month-year
    df["Length_of_Stay"] = (df["Discharge_Date"] - df["Admission_Date"]).dt.days  # Compute stay length
    return df

df = load_data()

# Sidebar
st.sidebar.title("📊 Filters")
selected_diagnosis = st.sidebar.selectbox("Select Diagnosis", ["All"] + list(df["Diagnosis"].unique()))
selected_specialty = st.sidebar.multiselect("Select Doctor Specialty", df["Doctor_Specialty"].unique())

# if st.sidebar.button("Go to Data page"):
#     st.switch_page("pages/data.py")

# Apply filters
if selected_diagnosis != "All":
    df = df[df["Diagnosis"] == selected_diagnosis]
if selected_specialty:
    df = df[df["Doctor_Specialty"].isin(selected_specialty)]
    


# Title
st.title("🏥 Data-Driven Insights on Diagnoses, Patient Admissions and Treatment Costs")
st.divider()

# ---- 1️⃣ Monthly Admissions Trend ----
# st.subheader("📈 Monthly Patient Admissions")
# admissions_per_month = df.groupby("Admission_Month").size().reset_index(name="Admissions")
# fig1 = px.line(admissions_per_month, x="Admission_Month", y="Admissions",
#                title="Monthly Admissions Trend", markers=True)
# st.plotly_chart(fig1, use_container_width=True)

# discharges_per_month = df.groupby("Discharge_Month").size().reset_index(name="Discharge")
# fig6 = px.line(discharges_per_month, x="Discharge_Month", y="Discharge",
#                title="Monthly Discharge Trend", markers=True)
# st.plotly_chart(fig6, use_container_width=True)


st.subheader("📈 Monthly Patient Admissions and Discharges")

# Group admissions and discharges separately
admissions_per_month = df.groupby("Admission_Month").size().reset_index(name="Admissions")
discharges_per_month = df.groupby("Discharge_Month").size().reset_index(name="Discharges")

# Create line chart with both trends
fig1 = px.line(title="Monthly Admissions and Discharges Trend", markers=True)

# Add Admissions trend
fig1.add_scatter(x=admissions_per_month["Admission_Month"], y=admissions_per_month["Admissions"], 
                mode="lines+markers", name="Admissions")

# Add Discharges trend
fig1.add_scatter(x=discharges_per_month["Discharge_Month"], y=discharges_per_month["Discharges"], 
                mode="lines+markers", name="Discharges")

fig1.update_traces(line_shape="spline", line=dict(width=2))
st.plotly_chart(fig1, use_container_width=True)

st.divider()

# ---- 2️⃣ Diagnoses Distribution ----
st.subheader("🦠 Disease Burden Distribution")

diagnosis_counts = df["Diagnosis"].value_counts().reset_index()
diagnosis_counts.columns = ["Diagnosis", "Count"]
# Determine colors (highlight max in red)
colors = ["red" if i == 0 else "navy" for i in range(len(diagnosis_counts))]
fig2 = px.bar(diagnosis_counts, x="Diagnosis", y="Count",
              title="Most Common Diagnoses", text="Count",
              color=diagnosis_counts.index.map(lambda i: "Highest" if i == 0 else "Others"),
              color_discrete_map={"Highest": "red", "Others": "navy"})

fig2.update_traces(textposition="inside", textfont_size=12)
fig2.update_layout(showlegend=False)  # Disable color legend
st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ---- 3️⃣ Gender Distribution ----
st.subheader("⚧ Gender Distribution")

# Count gender occurrences
gender_counts = df["Gender"].value_counts().reset_index()
gender_counts.columns = ["Gender", "Count"]

# Create two columns for side-by-side display
col1, col2 = st.columns(2)

# Pie Chart
with col1:
    fig_pie = px.pie(
        gender_counts, 
        names="Gender", 
        values="Count", 
        title="% Gender Distribution", 
        color="Gender", 
        color_discrete_sequence=["navy", skyblue,"red"]  # Customize colors
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# Bar Chart

with col2:
    fig_bar = px.bar(
        gender_counts, 
        x="Gender", 
        y="Count", 
        text="Count", 
        color="Gender", 
        color_discrete_sequence=["navy", skyblue,"red"],  # Customize colors
        title="Gender Distribution by Number"
    )

    # Customize layout
    fig_bar.update_traces(textposition="inside", textfont_size=14)
    fig_bar.update_layout(
        # xaxis_title="Gender", 
        yaxis_title="",  # Remove axis title
        yaxis=dict(showgrid=False, showticklabels=False),  # Hide gridlines and scale
        template="plotly_white",
        showlegend=False
    )

    # Show the plot
    st.plotly_chart(fig_bar, use_container_width=True)
    
# Count occurrences of each diagnosis by gender
df_diag_gender = df.groupby(["Diagnosis", "Gender"]).size().reset_index(name="Count")

# Create grouped bar plot
fig3 = px.bar(df_diag_gender, 
             x="Diagnosis", 
             y="Count", 
             color="Gender", 
             barmode="group",  # Groups bars by gender
             text="Count",
             title="Diagnosis Distribution by Gender",
             color_discrete_map={"Male": "navy", "Female": skyblue,"Other":"red"})  # Custom gender colors

# Customize layout
fig3.update_traces(textposition="outside", textfont_size=10)
fig3.update_layout(
    xaxis_title="Diagnosis", 
    yaxis_title="",  # Remove y-axis title
    yaxis=dict(showgrid=False, showticklabels=False),  # Hide gridlines and scale
    xaxis=dict(tickangle=-45),  # Rotate x-axis labels for better readability
    
)

# Show plot
st.plotly_chart(fig3, use_container_width=True)

st.divider()

st.subheader("📆 Age Diagnoses Analysis")

# Ensure Age column is numeric
df["Age"] = pd.to_numeric(df["Age"], errors="coerce")

# Drop NaN values from Age
df = df.dropna(subset=["Age"])

# Convert Age column to integer (if necessary)
df["Age"] = df["Age"].astype(int)

# Define age bins (grouped every 5 years)
bins = list(range(0, df["Age"].max() + 5, 5))  
labels = [f"{b}-{b+4}" for b in bins[:-1]]  # Ensure labels are strings

# Categorize patients into age groups
df["Age_Group"] = pd.cut(df["Age"], bins=bins, labels=labels, right=False)

# Count diagnoses by age group
df_age_diag = df.groupby(["Age_Group"]).size().reset_index(name="Count")
df_age_diag = df_age_diag.sort_values(by="Count", ascending=False)
top_3_groups = df_age_diag["Age_Group"].head(3).tolist()
df_age_diag["Color"] = df_age_diag["Age_Group"].apply(lambda x: "red" if x in top_3_groups else "navy")

# Create bar chart
fig4 = px.bar(df_age_diag, 
             x="Age_Group", 
             y="Count", 
             text="Count",
             title="Age Groups with Highest Diagnoses",
             color="Color",
             color_discrete_map={"red": "red", "navy": "navy"})  

# Add a **VERTICAL** dotted line separating the top 3 groups
fig4.add_shape(
    type="line",
    x0=2.5, x1=2.5,  # Position at the boundary of the top 3
    y0=0, y1=df_age_diag["Count"].max() * 1.1,  
    line=dict(color="red", width=1, dash="dot")
)

# Customize layout
fig4.update_traces(textposition="inside", textfont_size=12)
fig4.update_layout(
    xaxis_title="Age Group (5-year bins)", 
    yaxis_title="Total Diagnoses",
    xaxis=dict(type="category"),  
    template="plotly_white",
    showlegend=False  
)

st.plotly_chart(fig4, use_container_width=True)

st.divider()

st.subheader("🩺 Readmission Status Analysis")
 #Group by Readmission_Status
readmission_counts = df["Readmission_Status"].value_counts().reset_index()
readmission_counts.columns = ["Readmission_Status", "Count"]

# Create First Chart (Readmission Status)
fig1 = px.bar(readmission_counts, x="Readmission_Status", y="Count", text="Count",
              title="Readmission Status Count", color="Readmission_Status",
              color_discrete_sequence=["navy", skyblue])

# Create Second Chart (Readmission Status vs Diagnosis)
fig2 = px.histogram(df, x="Diagnosis", color="Readmission_Status", barmode="group",
                    title="Readmission Status by Diagnosis",
                    color_discrete_sequence=[skyblue , "navy"])

# Display charts side by side using columns
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.plotly_chart(fig2, use_container_width=True)
    
    
st.divider()

st.subheader("💰 Treatment Cost Analysis")

# Ensure 'Treatment_Cost' is numeric
df["Treatment_Cost"] = pd.to_numeric(df["Treatment_Cost"], errors="coerce")

# Aggregate total treatment cost per diagnosis
df_treatment_cost = df.groupby("Diagnosis", as_index=False)["Treatment_Cost"].sum()

# Sort by highest cost
df_treatment_cost = df_treatment_cost.sort_values(by="Treatment_Cost", ascending=False)

# Identify diagnosis with the highest cost
max_diagnosis = df_treatment_cost.iloc[0]

# Apply currency formatting
df_treatment_cost["Formatted_Cost"] = df_treatment_cost["Treatment_Cost"].apply(
    lambda x: f"₦{x:,.2f}" if pd.notnull(x) else "N/A"
)

# Assign colors (highlight highest-cost diagnosis)
df_treatment_cost["Color"] = df_treatment_cost["Diagnosis"].apply(
    lambda x: "red" if x == max_diagnosis["Diagnosis"] else "navy"
)

# Create bar chart
fig5 = px.bar(
    df_treatment_cost,
    y="Diagnosis",
    x="Treatment_Cost",
    text=df_treatment_cost["Formatted_Cost"],
    title="Total Treatment Cost by Diagnosis",
    orientation="h",
    color="Color",
    color_discrete_map={"red": "red", "navy": "navy"},
)

# Format the layout
fig5.update_traces(textposition="inside", textfont_size=12)
fig5.update_layout(
    xaxis_title="Total Cost (₦)",
    yaxis_title="Diagnosis",
    xaxis=dict(showgrid=False, zeroline=False),
    yaxis=dict(categoryorder="total ascending"),
    template="plotly_white",
    showlegend=False,
)

st.plotly_chart(fig5, use_container_width=True)


st.divider()
#Count occurrences of each Insurance Provider
st.subheader("🛡️ Insurance Provider Coverage")
insurance_counts = df["Insurance_Provider"].value_counts().reset_index()
insurance_counts.columns = ["Insurance_Provider", "Count"]

# Identify the provider with the highest count
max_provider = insurance_counts.iloc[0]["Insurance_Provider"]

# Assign colors: Highest count = red, others = navy
insurance_counts["Color"] = insurance_counts["Insurance_Provider"].apply(lambda x: "red" if x == max_provider else "navy")

# Create Bar Chart
fig = px.bar(insurance_counts, x="Insurance_Provider", y="Count", text="Count",
             title="Most Common Insurance Providers",
             color="Color",
             color_discrete_map="identity")  # Keep custom colors

# Display the chart in Streamlit
st.plotly_chart(fig, use_container_width=True)




# Footer
st.write("🛠️ **Built by Nensok Obadiah Gofup**")

