import React from 'react';
import { ArrowUp, ShieldAlert } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="border-t border-white/10 bg-black/50 backdrop-blur-lg mt-12 py-8">
      <div className="max-w-7xl mx-auto px-6 sm:px-12 flex flex-col md:flex-row items-center justify-between gap-6">
        
        <div className="flex flex-col items-center md:items-start gap-2">
          <a href="#home" className="flex items-center gap-2 text-xl font-bold tracking-tight text-white">
            <ShieldAlert className="text-primary" />
            <span>CarDD<span className="text-primary">.ai</span></span>
          </a>
          <p className="text-sm text-foreground/50">
            Automating Insurance Claims through deep learning.
          </p>
        </div>
        
        <div className="flex items-center gap-6 text-sm text-foreground/60">
          <a href="#about" className="hover:text-white transition-colors">About</a>
          <a href="#pipeline" className="hover:text-white transition-colors">Pipeline</a>
          <a href="#technologies" className="hover:text-white transition-colors">Technologies</a>
        </div>
        
        <div className="flex items-center gap-4">
          <button 
            onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
            className="w-10 h-10 rounded-full bg-white/5 border border-white/10 flex items-center justify-center text-foreground/80 hover:text-white hover:bg-white/10 transition-all"
            aria-label="Back to top"
          >
            <ArrowUp size={18} />
          </button>
        </div>
        
      </div>
      <div className="mt-8 text-center text-xs text-foreground/40">
        &copy; {new Date().getFullYear()} CarDD AI Engine.
      </div>
    </footer>
  );
};

export default Footer;
