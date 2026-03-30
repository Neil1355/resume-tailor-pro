import { useState, useCallback, useRef } from "react";
import { motion } from "framer-motion";
import { Download } from "lucide-react";
import { toast } from "sonner";
import { tailorResume } from "@/api/resumeTailorClient";
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
  const intervalRef = useRef<ReturnType<typeof setInterval>>();

  const canTailor = file && jobDescription.trim().length > 10;

  const handleTailor = useCallback(async () => {
    if (!file || !canTailor) return;
    setLoading(true);
    setProgress(0);
    setTailored(false);

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
        toast.success("Resume tailored successfully!", {
          description: "Your document is ready for export.",
        });
        // Store result for download
        sessionStorage.setItem("tailorResult", JSON.stringify(result));
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

  const handleExport = (format: "pdf" | "docx") => {
    setExportOpen(false);
    toast.success(`Downloading as ${format.toUpperCase()}...`);
    // In production, trigger the actual download here
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
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4 }}
            >
              <button
                onClick={() => setExportOpen(true)}
                className="w-full h-12 rounded-xl border border-success/40 bg-success/10 text-success font-medium flex items-center justify-center gap-2 hover:bg-success/20 transition-colors"
              >
                <Download className="w-4 h-4" />
                Export Tailored Resume
              </button>
            </motion.div>
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
