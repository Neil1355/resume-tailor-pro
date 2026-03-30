import { useState } from "react";

interface JobDescriptionInputProps {
  value: string;
  onChange: (value: string) => void;
}

const JobDescriptionInput = ({ value, onChange }: JobDescriptionInputProps) => {
  const [focused, setFocused] = useState(false);

  return (
    <div className={`glass-card transition-all duration-500 ${focused ? "glow-ring" : ""}`}>
      <div className="p-5 pb-3">
        <label className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
          Job Description
        </label>
      </div>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onFocus={() => setFocused(true)}
        onBlur={() => setFocused(false)}
        placeholder="Paste the job description here to tailor your resume..."
        rows={8}
        className="w-full bg-transparent text-foreground placeholder:text-muted-foreground/50 px-5 pb-5 resize-none focus:outline-none text-sm leading-relaxed font-mono"
        style={{ fontFamily: "'JetBrains Mono', monospace" }}
      />
    </div>
  );
};

export default JobDescriptionInput;
