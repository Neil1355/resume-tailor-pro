import { useState, useRef, useCallback } from "react";
import { motion } from "framer-motion";
import { Upload, FileText, X } from "lucide-react";

interface UploadZoneProps {
  onFileSelect: (file: File | null) => void;
  file: File | null;
}

const UploadZone = ({ onFileSelect, file }: UploadZoneProps) => {
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrag = useCallback((e: React.DragEvent, entering: boolean) => {
    e.preventDefault();
    e.stopPropagation();
    setDragging(entering);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setDragging(false);
      const droppedFile = e.dataTransfer.files?.[0];
      if (droppedFile && isValidFile(droppedFile)) {
        onFileSelect(droppedFile);
      }
    },
    [onFileSelect]
  );

  const isValidFile = (f: File) =>
    f.type === "application/pdf" ||
    f.type === "application/vnd.openxmlformats-officedocument.wordprocessingml.document";

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected && isValidFile(selected)) {
      onFileSelect(selected);
    }
  };

  const removeFile = (e: React.MouseEvent) => {
    e.stopPropagation();
    onFileSelect(null);
    if (inputRef.current) inputRef.current.value = "";
  };

  return (
    <div
      className={`upload-zone p-8 text-center ${dragging ? "dragging" : ""}`}
      onClick={() => inputRef.current?.click()}
      onDragOver={(e) => handleDrag(e, true)}
      onDragEnter={(e) => handleDrag(e, true)}
      onDragLeave={(e) => handleDrag(e, false)}
      onDrop={handleDrop}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.docx"
        className="hidden"
        onChange={handleChange}
      />

      {file ? (
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          className="flex items-center justify-center gap-3"
        >
          <FileText className="w-8 h-8 text-primary" />
          <div className="text-left">
            <p className="text-foreground font-medium truncate max-w-[200px]">
              {file.name}
            </p>
            <p className="text-muted-foreground text-sm">
              {(file.size / 1024).toFixed(1)} KB
            </p>
          </div>
          <button
            onClick={removeFile}
            className="ml-2 p-1.5 rounded-lg bg-secondary hover:bg-destructive/20 text-muted-foreground hover:text-destructive transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </motion.div>
      ) : (
        <div className="space-y-3">
          <div className="mx-auto w-14 h-14 rounded-2xl bg-secondary flex items-center justify-center">
            <Upload className="w-6 h-6 text-primary" />
          </div>
          <div>
            <p className="text-foreground font-medium">
              Drop your resume here
            </p>
            <p className="text-muted-foreground text-sm mt-1">
              PDF or DOCX · Max 10MB
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default UploadZone;
