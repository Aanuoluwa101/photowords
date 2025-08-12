import React, { useEffect, useState } from "react";
import axiosInstance from "../utils/axiosInstance";

const AdminGroups = () => {
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [success, setSuccess] = useState(null);
  const [error, setError] = useState(null);

  const [imageTags, setImageTags] = useState([]);

  const [newGroup, setNewGroup] = useState({
    answer: "",
    difficulty: "EASY",
    hint: "",
    images: [],
  });

  const [imageInput, setImageInput] = useState({
    tag: "",
    start_index: "",
    end_index: "",
    position: "",
  });

  const baseUrl = process.env.REACT_APP_API_BASE_URL;

  const fetchGroups = async () => {
    try {
      setLoading(true);
      setError(null);
      const token = localStorage.getItem("id_token");
      const response = await axiosInstance.get(`${baseUrl}/groups/`, {
        headers: { Authorization: token },
      });
      setGroups(response.data);
      setSuccess("Groups loaded successfully");
      setTimeout(() => setSuccess(null), 4000);
    } catch (err) {
      setError("Failed to load groups");
      setError(() => setError(null), 4000);
    } finally {
      setLoading(false);
    }
  };


  // Inside your component
const handleDeleteGroup = async (groupId) => {
  try {
    if (!window.confirm(`Are you sure you want to delete group "${groupId}"?`)) return;
    const token = localStorage.getItem("id_token");

    const response = await axiosInstance.delete(
      `${baseUrl}/groups?id=${groupId}`,
      {
        headers: {
          Authorization: token,
        },
      }
    );

    if (response.status === 204) {
      setSuccess("Group deleted successfully!");
      setTimeout(() => setSuccess(null), 4000);
      fetchGroups(); // refresh list
    } else {
      throw new Error("Unexpected response from server.");
    }
  } catch (error) {
    console.error("Error deleting group:", error);

    let message = "Failed to delete group. Please try again.";
    if (error.response?.data?.error) {
      message = error.response.data.error;
    }

    setError(message);
    setTimeout(() => setError(null), 4000);
  }
};


  const fetchImages = async () => {
    try {
      const token = localStorage.getItem("id_token");
      const response = await axiosInstance.get(`${baseUrl}/images`, {
        headers: { Authorization: token },
      });
      setImageTags(response.data.images || []);
    } catch (error) {
      console.error("Error fetching images:", error);
      let message = "Failed to load images. Please try again.";
      if (error.response?.data?.error) {
        message = error.response.data.error;
      }
      setError(message);
      setTimeout(() => setError(null), 4000);
    }
  };

  useEffect(() => {
    fetchGroups();
    fetchImages(); // fetch tags on load
  }, []);

  const handleAddImage = () => {
    if (
      !imageInput.tag ||
      imageInput.start_index === "" ||
      imageInput.end_index === "" ||
      imageInput.position === ""
    ) {
      setError("Please fill in all image fields");
      setTimeout(() => setError(null), 4000);
      return;
    }
    setNewGroup((prev) => ({
      ...prev,
      images: [
        ...prev.images,
        {
          ...imageInput,
          start_index: Number(imageInput.start_index),
          end_index: Number(imageInput.end_index),
          position: Number(imageInput.position),
        },
      ],
    }));
    setImageInput({ tag: "", start_index: "", end_index: "", position: "" });
  };

  const handleCreateGroup = async (e) => {
    e.preventDefault();
    try {
      setError(null);
      setSuccess(null);
      const token = localStorage.getItem("id_token");
      console.log(newGroup)
      const response = await axiosInstance.post(`${baseUrl}/groups/`, newGroup, {
        headers: { Authorization: token },
      });
      setSuccess(response.data.message || "Group created successfully!");
      setNewGroup({ answer: "", difficulty: "EASY", hint: "", images: [] });
      fetchGroups();
    } catch (err) {
      let message = "Failed to create group.";
      if (err.response?.data?.error) {
        message = err.response.data.error;
      }
      setError(message);
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Groups</h1>

      {success && (
        <p className="mb-2 text-green-600 bg-green-100 p-2 rounded">{success}</p>
      )}
      {error && (
        <p className="mb-2 text-red-600 bg-red-100 p-2 rounded">{error}</p>
      )}

      {/* Create New Group Form */}
      <form
        onSubmit={handleCreateGroup}
        className="mb-6 p-4 border rounded bg-white shadow"
      >
        <h2 className="text-lg font-semibold mb-2">Create New Group</h2>

        <div className="mb-2">
          <input
            type="text"
            placeholder="Answer"
            value={newGroup.answer}
            onChange={(e) => setNewGroup({ ...newGroup, answer: e.target.value })}
            className="border px-2 py-1 rounded w-full"
          />
        </div>

        <div className="mb-2">
          <select
            value={newGroup.difficulty}
            onChange={(e) =>
              setNewGroup({ ...newGroup, difficulty: e.target.value })
            }
            className="border px-2 py-1 rounded w-full"
          >
            <option value="EASY">EASY</option>
            <option value="MEDIUM">MEDIUM</option>
            <option value="HARD">HARD</option>
          </select>
        </div>

        <div className="mb-2">
          <input
            type="text"
            placeholder="Hint"
            value={newGroup.hint}
            onChange={(e) => setNewGroup({ ...newGroup, hint: e.target.value })}
            className="border px-2 py-1 rounded w-full"
          />
        </div>

        {/* Add Images */}
        <div className="mb-2 border p-2 rounded">
          <h3 className="font-medium mb-2">Add Images</h3>
          <div className="grid grid-cols-2 gap-2 mb-2">
            <select
              value={imageInput.tag}
              onChange={(e) =>
                setImageInput({ ...imageInput, tag: e.target.value })
              }
              className="border px-2 py-1 rounded"
            >
              <option value="">Select Tag</option>
              {imageTags.map((tag, idx) => (
                <option key={idx} value={tag}>
                  {tag}
                </option>
              ))}
            </select>
            <input
              type="number"
              placeholder="Start Index"
              value={imageInput.start_index}
              onChange={(e) =>
                setImageInput({ ...imageInput, start_index: e.target.value })
              }
              className="border px-2 py-1 rounded"
            />
            <input
              type="number"
              placeholder="End Index"
              value={imageInput.end_index}
              onChange={(e) =>
                setImageInput({ ...imageInput, end_index: e.target.value })
              }
              className="border px-2 py-1 rounded"
            />
            <input
              type="number"
              placeholder="Position"
              value={imageInput.position}
              onChange={(e) =>
                setImageInput({ ...imageInput, position: e.target.value })
              }
              className="border px-2 py-1 rounded"
            />
          </div>
          <button
            type="button"
            onClick={handleAddImage}
            className="bg-blue-600 text-white px-3 py-1 rounded"
          >
            Add Image
          </button>

          {newGroup.images.length > 0 && (
            <ul className="mt-2 list-disc list-inside text-sm">
              {newGroup.images.map((img, i) => (
                <li key={i}>
                  {img.tag} (Pos: {img.position}, Index: {img.start_index}-
                  {img.end_index})
                </li>
              ))}
            </ul>
          )}
        </div>

        <button
          type="submit"
          className="bg-green-600 text-white px-4 py-2 rounded"
        >
          Create Group
        </button>
      </form>

    {/* Total Groups Card */}
    {!loading && (
      <div className="flex justify-center mb-4">
        <div className="bg-white shadow-md rounded-lg p-4 w-full max-w-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-800 text-center">
            Total Groups
          </h3>
          <p className="text-2xl font-bold text-blue-600 text-center">
            {groups.length}
          </p>
        </div>
      </div>
    )}

    {/* Group List */}
    {loading ? (
      <p>Loading groups...</p>
    ) : groups.length === 0 ? (
      <p>No groups found.</p>
    ) : (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {groups.map((group) => (
          <div
            key={group.id}
            className="border rounded-lg p-4 shadow-sm bg-white"
          >
            <h2 className="text-lg font-semibold mb-1">{group.answer}</h2>
            <p className="text-sm text-gray-600">
              Difficulty:{" "}
              <span className="font-medium">{group.difficulty}</span>
            </p>
            <p className="text-sm text-gray-600 mb-2">
              Hint: {group.hint || "No hint provided"}
            </p>
            <div className="mb-2">
              <p className="text-sm font-semibold">Images:</p>
              {group.images.length > 0 ? (
                <ul className="list-disc list-inside text-sm text-gray-700">
                  {group.images.map((img, index) => (
                    <li key={index}>
                      Tag: {img.tag}, Position: {img.position}, Index:{" "}
                      {img.start_index} - {img.end_index}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-gray-500">No images</p>
              )}
            </div>
            <p className="text-xs text-gray-500">
              Created: {new Date(group.created_at).toLocaleString()}
            </p>
            <p className="text-xs text-gray-500">By: {group.created_by}</p>

            {/* Delete Button */}
            <button
              onClick={() => handleDeleteGroup(group.id)}
              className="mt-3 px-3 py-1 text-sm text-white bg-red-500 rounded hover:bg-red-600"
            >
              Delete
            </button>
          </div>
        ))}
      </div>
    )}
    </div>
  );
};

export default AdminGroups;
