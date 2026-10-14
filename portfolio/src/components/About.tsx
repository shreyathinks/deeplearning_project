import React from 'react';
import { motion } from 'framer-motion';
import { Target, Image as ImageIcon, Zap, ShieldCheck } from 'lucide-react';

const stats = [
  { label: 'Classes Detected', value: '6', icon: Target },
  { label: 'High Res Output', value: '1024px', icon: ImageIcon },
  { label: 'Inference Speed', value: '<2s', icon: Zap },
  { label: 'Severity Levels', value: '3', icon: ShieldCheck },
];

const About = () => {
  return (
    <section id="about" className="py-24 relative">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6 }}
      >
        <div className="flex flex-col items-center mb-16">
          <h2 className="text-3xl md:text-5xl font-bold tracking-tight mb-4">The Problem & Solution</h2>
          <div className="w-24 h-1 bg-gradient-to-r from-primary to-accent rounded-full" />
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
          <div className="glass-card p-8 relative overflow-hidden group">
            <div className="absolute inset-0 bg-gradient-to-br from-primary/10 to-accent/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            <h3 className="text-2xl font-semibold mb-4">Automating Insurance Claims</h3>
            <p className="text-foreground/80 leading-relaxed mb-6">
              Evaluating vehicle damage is traditionally a slow, manual process prone to human error and subjectivity. The CarDD AI Engine was developed to completely automate this pipeline for insurance companies and repair shops.
            </p>
            <p className="text-foreground/80 leading-relaxed">
              By combining three state-of-the-art Neural Networks into a single orchestrated pipeline, we can accurately detect the type of damage, trace its exact physical boundaries, and classify its severity in under 2 seconds.
            </p>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            {stats.map((stat, i) => {
              const Icon = stat.icon;
              return (
                <motion.div 
                  key={stat.label}
                  initial={{ opacity: 0, scale: 0.9 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.4, delay: i * 0.1 }}
                  className="glass-card p-6 flex flex-col items-center text-center gap-3 hover:border-primary/50 transition-colors"
                >
                  <Icon className="text-primary w-8 h-8" />
                  <div className="text-3xl font-bold text-white">{stat.value}</div>
                  <div className="text-xs text-foreground/60 uppercase tracking-wider font-semibold">{stat.label}</div>
                </motion.div>
              )
            })}
          </div>
        </div>
      </motion.div>
    </section>
  );
};

export default About;
