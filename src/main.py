import sys
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler, StandardScaler, PCA
from pyspark.ml.clustering import KMeans
from dotenv import load_dotenv
import os
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType
from utils import generate_offer

# Load environment variables from .env file
load_dotenv('/app/.env')

# Read environment variables
storage_account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
storage_account_key = os.getenv("AZURE_STORAGE_ACCOUNT_KEY")
container_name = os.getenv("AZURE_BLOB_CONTAINER")
file_name = os.getenv("AZURE_BLOB_FILE")

# Check if all required environment variables are set
if not all([storage_account_name, storage_account_key, container_name, file_name]):
    print("ERROR: One or more Azure environment variables are not set correctly.")
    sys.exit(1)

# Packages required for Spark
packages_to_include = ",".join([
    "org.apache.hadoop:hadoop-azure:3.3.6",
    "com.microsoft.azure:azure-storage:8.6.6",
    "org.apache.hadoop:hadoop-client-runtime:3.3.6",
    "org.apache.hadoop:hadoop-client-api:3.3.6"
])

# Create SparkSession
print("Building SparkSession...")
spark = SparkSession.builder.appName("AzureReadTestWithPackages") \
    .config("spark.hadoop.fs.azure.account.key." + storage_account_name + ".blob.core.windows.net", storage_account_key) \
    .config("spark.jars.packages", packages_to_include) \
    .getOrCreate()

print("SparkSession created.")

# Azure Blob Storage path to the data
wasbs_path = f"wasbs://{container_name}@{storage_account_name}.blob.core.windows.net/{file_name}"

# Read data from Azure Blob Storage
print(f"Attempting to read from: {wasbs_path}")
df = spark.read.csv(wasbs_path, header=True, inferSchema=True)

# Show the first few rows of the data
df.show(5)

# --- PCA: Dimensionality Reduction ---
# Step 1: Select features for PCA
feature_columns = ['Age', 'Annual Income (k$)', 'Spending Score (1-100)']  # Based on your dataset's features

# Use VectorAssembler to combine features
assembler = VectorAssembler(inputCols=feature_columns, outputCol="features")
df_assembled = assembler.transform(df)

# Standardize the data
scaler = StandardScaler(inputCol="features", outputCol="scaled_features")
scaler_model = scaler.fit(df_assembled)
df_scaled = scaler_model.transform(df_assembled)

# Apply PCA for dimensionality reduction
pca = PCA(k=2, inputCol="scaled_features", outputCol="pca_features")
pca_model = pca.fit(df_scaled)
df_pca = pca_model.transform(df_scaled)

# Show PCA results
df_pca.select("CustomerID", "pca_features").show(5)

# --- KMeans: Clustering the data ---
kmeans = KMeans(k=4, featuresCol="pca_features", predictionCol="prediction")
model = kmeans.fit(df_pca)
df_kmeans = model.transform(df_pca)

# Show the resulting clusters
df_kmeans.select("CustomerID", "prediction").show(5)

# Register the UDF function
generate_offer_udf = udf(generate_offer, StringType())

# Add offers to the DataFrame
df_kmeans = df_kmeans.withColumn("offer", generate_offer_udf(df_kmeans["prediction"]))

# Show the results along with the offers
df_kmeans.select("CustomerID", "prediction", "offer").show(5)

# Stop SparkSession after processing
print("Stopping SparkSession.")
spark.stop()
