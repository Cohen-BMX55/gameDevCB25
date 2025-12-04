import express from "express";
import multer from "multer";
import { Vibrant } from "node-vibrant";
import path from "path";
import fs from "fs";

if (!fs.existsSync("uploads")) {
  fs.mkdirSync("uploads");
}

const app = express();
const upload = multer({ dest: "uploads/" });

app.use(express.static("public"));

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

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

