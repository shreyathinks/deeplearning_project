import React from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, Sparkles } from 'lucide-react';

const Hero = () => {
  return (
    <section id="home" className="min-h-[90vh] flex flex-col justify-center relative pt-20">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
        
        <motion.div 
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="flex flex-col gap-6"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass border border-white/10 w-max text-sm font-medium text-primary">
            <Sparkles size={16} className="text-accent" />
            <span>AI • Computer Vision • Automation</span>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight leading-[1.1]">
            Automated <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent">Damage Assessment</span><br />
            Engine.
          </h1>
          
          <p className="text-lg md:text-xl text-foreground/70 max-w-xl leading-relaxed">
            An end-to-end Machine Learning pipeline utilizing YOLOv8 and Segformer to instantly detect, trace, and evaluate vehicle damage for automated insurance claims.
          </p>
          
          <div className="flex items-center gap-4 mt-4">
            <a href="http://127.0.0.1:5000" target="_blank" rel="noreferrer" className="px-8 py-4 rounded-full bg-primary hover:bg-primary/90 text-white font-semibold transition-all hover:scale-105 shadow-[0_0_20px_rgba(59,130,246,0.3)] flex items-center gap-2">
              Launch Live Demo <ArrowRight size={18} />
            </a>
            <a href="#pipeline" className="px-8 py-4 rounded-full glass border-white/20 hover:bg-white/10 font-semibold transition-all hover:scale-105">
              See How It Works
            </a>
          </div>
        </motion.div>
        
        <motion.div 
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 1, ease: "easeOut", delay: 0.2 }}
          className="relative h-[500px] hidden lg:flex items-center justify-center"
        >
          {/* Futuristic Abstract Element representing computer vision */}
          <div className="absolute inset-0 bg-gradient-to-tr from-primary/20 to-accent/20 rounded-full blur-3xl animate-pulse" />
          <div className="relative w-80 h-80 rounded-2xl border border-white/10 glass flex items-center justify-center overflow-hidden shadow-2xl transform rotate-3 hover:rotate-0 transition-transform duration-500">
            <div className="absolute inset-0 bg-gradient-to-tr from-primary/10 to-accent/10 backdrop-blur-xl" />
            
            {/* Fake bounding box animation */}
            <div className="absolute top-1/4 left-1/4 w-1/2 h-1/2 border-2 border-primary/80 bg-primary/10 rounded" />
            <div className="absolute top-1/4 left-1/4 px-2 py-1 bg-primary text-xs font-bold text-white -translate-y-full rounded-t">
              damage: 0.98
            </div>
            
            {/* Scanner line */}
            <div className="absolute top-0 left-0 right-0 h-1 bg-accent/80 shadow-[0_0_15px_rgba(139,92,246,1)] animate-[scan_3s_ease-in-out_infinite]" />
          </div>
        </motion.div>
        
      </div>
    </section>
  );
};

export default Hero;
