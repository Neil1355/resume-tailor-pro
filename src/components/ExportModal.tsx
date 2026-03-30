import { motion, AnimatePresence } from "framer-motion";
import { FileText, FileDown, X } from "lucide-react";

interface ExportModalProps {
  open: boolean;
  onClose: () => void;
  onExport: (format: "pdf" | "docx") => void;
}

const ExportModal = ({ open, onClose, onExport }: ExportModalProps) => {
  return (
    <AnimatePresence>
      {open && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
        >
          {/* Backdrop */}
          <motion.div
            className="absolute inset-0 bg-background/80 backdrop-blur-sm"
            onClick={onClose}
          />

          {/* Modal */}
          <motion.div
            initial={{ scale: 0.9, opacity: 0, y: 20 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            exit={{ scale: 0.9, opacity: 0, y: 20 }}
            transition={{ type: "spring", damping: 25, stiffness: 300 }}
            className="glass-card p-8 w-full max-w-md relative z-10"
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-foreground">
                Export Resume
              </h2>
              <button
                onClick={onClose}
                className="p-2 rounded-lg bg-secondary hover:bg-border text-muted-foreground hover:text-foreground transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <p className="text-muted-foreground text-sm mb-6">
              Choose your preferred format to download your tailored resume.
            </p>

            <div className="grid grid-cols-2 gap-4">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => onExport("pdf")}
                className="glass-card p-6 flex flex-col items-center gap-3 hover:border-destructive/50 transition-colors group"
              >
                <div className="w-14 h-14 rounded-2xl bg-destructive/15 flex items-center justify-center group-hover:bg-destructive/25 transition-colors">
                  <FileDown className="w-7 h-7 text-destructive" />
                </div>
                <div className="text-center">
                  <p className="font-semibold text-foreground">PDF</p>
                  <p className="text-xs text-muted-foreground mt-0.5">
                    Best for sharing
                  </p>
                </div>
              </motion.button>

              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => onExport("docx")}
                className="glass-card p-6 flex flex-col items-center gap-3 hover:border-primary/50 transition-colors group"
              >
                <div className="w-14 h-14 rounded-2xl bg-primary/15 flex items-center justify-center group-hover:bg-primary/25 transition-colors">
                  <FileText className="w-7 h-7 text-primary" />
                </div>
                <div className="text-center">
                  <p className="font-semibold text-foreground">Word</p>
                  <p className="text-xs text-muted-foreground mt-0.5">
                    Best for editing
                  </p>
                </div>
              </motion.button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default ExportModal;
