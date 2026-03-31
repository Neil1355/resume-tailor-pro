import { useState, useCallback, useRef } from "react";
import { motion } from "framer-motion";
import { Download } from "lucide-react";
import { toast } from "sonner";
import {
  downloadTailoredResume,
  tailorResume,
  type TailorResponse,
} from "@/api/resumeTailorClient";
import UploadZone from "@/components/UploadZone";
import JobDescriptionInput from "@/components/JobDescriptionInput";
import TailorButton from "@/components/TailorButton";
import ExportModal from "@/components/ExportModal";

const fadeInUp = {
  hidden: { opacity: 0, y: 30 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.15, duration: 0.6, ease: [0.22, 1, 0.36, 1] as [number, number, number, number] },
  }),
};

const Index = () => {
  const [file, setFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [tailored, setTailored] = useState(false);
  const [exportOpen, setExportOpen] = useState(false);
  const [showChanges, setShowChanges] = useState(false);
  const [tailorResult, setTailorResult] = useState<TailorResponse | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval>>();

  const canTailor = file && jobDescription.trim().length > 10;

  const handleTailor = useCallback(async () => {
    if (!file || !canTailor) return;
    setLoading(true);
    setProgress(0);
    setTailored(false);
    setShowChanges(false);
    setTailorResult(null);

    // Simulate progress while waiting for API
    intervalRef.current = setInterval(() => {
      setProgress((p) => (p >= 90 ? 90 : p + Math.random() * 12));
    }, 300);

    try {
      const result = await tailorResume(jobDescription);

      clearInterval(intervalRef.current);
      setProgress(100);

      setTimeout(() => {
        setLoading(false);
        setTailored(true);
        setTailorResult(result);
        toast.success("Resume tailored successfully!", {
          description: "Your document is ready for export.",
        });
      }, 500);
    } catch (error) {
      clearInterval(intervalRef.current);
      setLoading(false);
      setProgress(0);
      toast.error("Something went wrong", {
        description: error instanceof Error ? error.message : "Could not tailor resume. Please try again.",
      });
    }
  }, [file, jobDescription, canTailor]);

  const previewRows = tailorResult
    ? Object.keys(tailorResult.original_bullets)
        .sort()
        .map((tag) => {
          const original = tailorResult.original_bullets[tag] || "";
          const updated = tailorResult.tailored_bullets[tag] || original;
          return {
            tag,
            original,
            updated,
            changed: original.trim() !== updated.trim(),
          };
        })
    : [];

  const handleExport = async (format: "pdf" | "docx") => {
    setExportOpen(false);
    try {
      await downloadTailoredResume(format);
      toast.success(`Downloading as ${format.toUpperCase()}...`);
    } catch (error) {
      toast.error("Download failed", {
        description:
          error instanceof Error
            ? error.message
            : "Could not download the requested file.",
      });
    }
  };

  return (
    <div className="gradient-bg min-h-screen flex flex-col">
      {/* Header */}
      <motion.header
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="pt-12 pb-4 text-center"
      >
        <h1 className="text-3xl md:text-4xl font-bold text-foreground tracking-tight">
          Resume<span className="text-primary">Tailor</span>
        </h1>
        <p className="text-muted-foreground mt-2 text-sm max-w-md mx-auto">
          Upload your resume and paste the job description — we'll optimize it
          for maximum impact.
        </p>
      </motion.header>

      {/* Main content */}
      <main className="flex-1 flex items-start justify-center px-4 pb-12 pt-6">
        <div className="w-full max-w-xl space-y-5">
          <motion.div
            custom={0}
            variants={fadeInUp}
            initial="hidden"
            animate="visible"
          >
            <UploadZone file={file} onFileSelect={setFile} />
          </motion.div>

          <motion.div
            custom={1}
            variants={fadeInUp}
            initial="hidden"
            animate="visible"
          >
            <JobDescriptionInput
              value={jobDescription}
              onChange={setJobDescription}
            />
          </motion.div>

          <motion.div
            custom={2}
            variants={fadeInUp}
            initial="hidden"
            animate="visible"
          >
            <TailorButton
              onClick={handleTailor}
              loading={loading}
              progress={progress}
              disabled={!canTailor}
            />
          </motion.div>

          {/* Export button */}
          {tailored && (
            <>
              <motion.div
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4 }}
                className="grid grid-cols-1 sm:grid-cols-2 gap-3"
              >
                <button
                  onClick={() => setShowChanges((prev) => !prev)}
                  className="w-full h-12 rounded-xl border border-primary/40 bg-primary/10 text-primary font-medium flex items-center justify-center gap-2 hover:bg-primary/20 transition-colors"
                >
                  {showChanges ? "Hide What's Changed" : "See What's Changed"}
                </button>

                <button
                  onClick={() => setExportOpen(true)}
                  className="w-full h-12 rounded-xl border border-success/40 bg-success/10 text-success font-medium flex items-center justify-center gap-2 hover:bg-success/20 transition-colors"
                >
                  <Download className="w-4 h-4" />
                  Export Tailored Resume
                </button>
              </motion.div>

              {showChanges && tailorResult && (
                <motion.div
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                  className="glass-card p-4 md:p-5 space-y-3"
                >
                  <div className="flex items-center justify-between">
                    <h3 className="text-base font-semibold text-foreground">What Changed</h3>
                    <span className="text-xs text-muted-foreground">
                      {previewRows.filter((r) => r.changed).length} of {previewRows.length} bullets updated
                    </span>
                  </div>

                  <div className="space-y-3 max-h-[340px] overflow-auto pr-1">
                    {previewRows.map((row) => (
                      <div key={row.tag} className="rounded-lg border border-border/70 bg-secondary/30 p-3">
                        <div className="flex items-center justify-between mb-2">
                          <p className="text-xs uppercase tracking-wider text-muted-foreground">{row.tag}</p>
                          <span
                            className={`text-[11px] px-2 py-0.5 rounded-full ${
                              row.changed
                                ? "bg-success/20 text-success"
                                : "bg-muted text-muted-foreground"
                            }`}
                          >
                            {row.changed ? "Updated" : "Unchanged"}
                          </span>
                        </div>
                        <p className="text-xs text-muted-foreground mb-1">Original</p>
                        <p className="text-sm text-foreground/90">{row.original}</p>
                        <p className="text-xs text-muted-foreground mt-3 mb-1">Tailored</p>
                        <p className="text-sm text-foreground">{row.updated}</p>
                      </div>
                    ))}
                  </div>
                </motion.div>
              )}
            </>
          )}
        </div>
      </main>

      <ExportModal
        open={exportOpen}
        onClose={() => setExportOpen(false)}
        onExport={handleExport}
      />
    </div>
  );
};

export default Index;
