import { motion, AnimatePresence } from "framer-motion";
import { Sparkles } from "lucide-react";

interface TailorButtonProps {
  onClick: () => void;
  loading: boolean;
  progress: number;
  disabled: boolean;
}

const TailorButton = ({ onClick, loading, progress, disabled }: TailorButtonProps) => {
  return (
    <div className="relative">
      <AnimatePresence mode="wait">
        {loading ? (
          <motion.div
            key="progress"
            initial={{ opacity: 0, scaleX: 0.8 }}
            animate={{ opacity: 1, scaleX: 1 }}
            exit={{ opacity: 0, scaleX: 0.8 }}
            className="progress-bar-track h-14 w-full"
          >
            <motion.div
              className="progress-bar-fill h-full flex items-center justify-center"
              initial={{ width: "0%" }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.4, ease: "easeOut" }}
            >
              <span className="text-primary-foreground font-semibold text-sm drop-shadow">
                {Math.round(progress)}%
              </span>
            </motion.div>
          </motion.div>
        ) : (
          <motion.button
            key="button"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            onClick={onClick}
            disabled={disabled}
            className="tailor-btn w-full h-14 flex items-center justify-center gap-2.5 text-base disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:translate-y-0 disabled:hover:shadow-none"
          >
            <Sparkles className="w-5 h-5" />
            Tailor Resume
          </motion.button>
        )}
      </AnimatePresence>
    </div>
  );
};

export default TailorButton;
