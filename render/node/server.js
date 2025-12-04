import express from "express";
import multer from "multer";
import Vibrant from "node-vibrant";
import path from "path";

const app = express();
const upload = multer({ dest: "uploads/" });

app.use(express.static("."));

app.post("/upload", upload.single("image"), async (req, res) => {
  try {
    const filePath = path.resolve(req.file.path);
    const palette = await Vibrant.from(filePath).getPalette();

    const colors = Object.values(palette)
      .filter(Boolean)
      .map(sw => sw.getHex());

    res.json(colors);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Failed to extract colors" });
  }
});

app.listen(3000, () => console.log("Server running on http://localhost:3000"));
