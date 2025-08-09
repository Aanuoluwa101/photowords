import React, { useEffect, useState } from "react";
// import axios from "axios";
import axiosInstance from "../utils/axiosInstance"; // adjust path as needed


const AdminImages = () => {
  const [imageTags, setImageTags] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [tagInput, setTagInput] = useState("");
  const [uploadUrl, setUploadUrl] = useState("");
  const [uploading, setUploading] = useState(false);
  const [success, setSuccess] = useState(null);


  const baseUrl = process.env.REACT_APP_API_BASE_URL;
  const cloudFrontBaseUrl = process.env.REACT_APP_CLOUD_FRONT_BASE_URL;

  const fetchImages = async () => {
    try {
      const token = localStorage.getItem("id_token");
      // console.log("Fetching images with token:", token);
      const response = await axiosInstance.get(`${baseUrl}/images`, {
        headers: {
          Authorization: token,
        },
      });
      setImageTags(response.data.images);
      // console.log("Fetched images:", response.data.images);
    } catch (error) {
      console.error("Error fetching images:", error);

      let message = "Failed to load images. Please try again.";
      if (error.response?.data?.error) {
        message = error.response.data.error;
      }

      setError(message);
      setTimeout(() => setError(null), 4000);
    } finally {
      setLoading(false);
    }
  };


const handleDelete = async (tag) => {
  try {
    if (!window.confirm(`Are you sure you want to delete "${tag}"?`)) return;
    const token = localStorage.getItem("id_token");

    const response = await axiosInstance.delete(`${baseUrl}/images?tag=${encodeURIComponent(tag)}`, {
      headers: {
        Authorization: token,
      },
    });

    setSuccess(response.data.message || "Image deleted successfully.");
    setTimeout(() => setSuccess(null), 4000);

    // Refresh the image list after successful delete
    fetchImages();

  } catch (error) {
    console.error("Error deleting image:", error);

    let message = "Failed to delete image. Please try again.";
    if (error.response?.data?.error) {
      message = error.response.data.error;
    }

    setError(message);
    setTimeout(() => setError(null), 4000);
  }
};


  const handleGetUploadUrl = async () => {
    if (!tagInput) {
      setError("Please enter a tag before getting upload URL.");
      setTimeout(() => setError(null), 4000);
      return;
    }

    try {
      const token = localStorage.getItem("id_token");
      const response = await axiosInstance.get(
        `${baseUrl}/images/get-upload-url?tag=${encodeURIComponent(tagInput)}`,
        {
          headers: {
            Authorization: token,
          },
        }
      );
      setUploadUrl(response.data.presignedUrl); // assuming the API returns { url: "..." }
    } catch (error) {
      console.error("Error getting upload URL:", error);
      let message = "Failed to get upload URL.";
      if (error.response?.data?.error) {
        message = error.response.data.error;
      }
      setError(message);
      setTimeout(() => setError(null), 4000);
    }
  };

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file || !uploadUrl) return;

    try {
      setUploading(true);
      const token = localStorage.getItem("id_token");

      await axiosInstance.put(uploadUrl, file, {
        headers: {
          // "Content-Type": file.type,
          tag: tagInput,
        },
      });

      setError(null);
      setSuccess("Image uploaded successfully!");
      setUploadUrl("");
      setTagInput("");
      fetchImages(); // Refresh list

      setTimeout(() => setSuccess(null), 4000);
    } catch (error) {
      console.error("Upload failed:", error);
      let message = "Upload failed.";
      if (error.response?.data?.error) {
        message = error.response.data.error;
      }
      setError(message);
      setTimeout(() => setError(null), 4000);
    } finally {
      setUploading(false);
    }
  };

  useEffect(() => {
    fetchImages();
  }, []);

  return (
    <div className="p-6">
      <div className="mb-4 flex justify-between items-center">
        <h1 className="text-2xl font-bold">Images</h1>
      </div>

      {error && (
        <div className="mb-4 bg-red-100 text-red-700 px-4 py-2 rounded">
          {error}
        </div>
      )}

      {success && (
        <div className="mb-4 bg-green-100 text-green-700 px-4 py-2 rounded">
          {success}
        </div>
      )}

      {/* Upload UI */}
      <div className="mb-6 p-4 bg-white shadow rounded border">
        <h2 className="text-lg font-semibold mb-2">Upload New Image</h2>
        <div className="flex items-center gap-2 mb-2">
          <input
            type="text"
            placeholder="Enter image tag"
            value={tagInput}
            onChange={(e) => setTagInput(e.target.value)}
            className="border px-2 py-1 rounded w-64"
          />
          <button
            onClick={handleGetUploadUrl}
            className="bg-blue-600 text-white px-3 py-1 rounded"
          >
            Get Upload URL
          </button>
        </div>

        {uploadUrl && (
          <div className="mb-2">
            <p className="text-sm font-medium">Upload URL:</p>
            <pre className="bg-gray-100 p-2 rounded overflow-x-auto">
              {uploadUrl}
            </pre>
          </div>
        )}

        {uploadUrl && (
          <div>
            <input
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              disabled={uploading}
            />
          </div>
        )}
      </div>

      {/* Total count */}
      <div className="mb-4">
        <div className="bg-gray-100 p-4 rounded shadow-md inline-block">
          <h2 className="text-lg font-semibold">Total Images</h2>
          <p className="text-xl">{imageTags.length}</p>
        </div>
      </div>

      {/* Image list */}
      {loading ? (
        <p>Loading...</p>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {imageTags.map((tag) => (
            <div
              key={tag}
              className="border p-2 rounded shadow hover:shadow-lg transition"
            >
              <img
                src={`${cloudFrontBaseUrl}/images/${tag}`}
                alt={tag}
                className="w-full h-48 object-cover rounded"
              />
              <div className="mt-2 flex justify-between items-center">
                <span className="text-sm font-medium">{tag}</span>
                <button
                  onClick={() => handleDelete(tag)}
                  className="text-red-600 text-sm hover:underline"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default AdminImages;
