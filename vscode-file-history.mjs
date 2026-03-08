import fs from "node:fs";
import path from "node:path";
import process from "node:process";

const dir = path.join(process.env.HOME, ".config", "Code", "User", "History");
const restoredFiles = [];

for (const item of fs.readdirSync(dir)) {
  const itemPath = path.join(dir, item);

  if (fs.statSync(itemPath).isDirectory()) {
    const entriesFile = path.join(itemPath, "entries.json");

    if (fs.statSync(entriesFile).isFile()) {
      const fileContent = fs.readFileSync(entriesFile, { encoding: "utf-8" });
      const { resource, entries } = JSON.parse(fileContent);

      entries.sort((a, b) => b.timestamp - a.timestamp);

      const latestCopy = entries[0].id;

      console.log(
        `Restoring resource '${resource}': '${latestCopy}' (${new Date(entries[0].timestamp).toISOString()}})`,
      );

      const restoredFile = path.join(
        process.cwd(),
        "restored",
        ...resource.replace(/^file\:\/\/\/media\/data\/Development\//g, "").split("/"),
      );
      const restoredDir = path.join("/", ...restoredFile.split("/").slice(0, -1));
      const fileName = restoredFile.split("/").pop();

      if (restoredFiles.includes(resource)) {
        console.log(`File ${resource} already restored. Skip.`);
      } else {
        console.log(`Create restoration directory '${restoredDir}'...`);
        fs.mkdirSync(restoredDir, { recursive: true });

        console.log(`Restore file '${restoredFile}' from '${path.join(itemPath, latestCopy)}'...`);
        fs.cpSync(path.join(itemPath, latestCopy), restoredFile);

        restoredFiles.push(resource);
      }
    } else {
      console.warn(`No entries file found in folder ${itemPath}`);
    }
  }
}
