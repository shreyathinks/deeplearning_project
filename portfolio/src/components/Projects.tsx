import React from 'react';
import { motion } from 'framer-motion';
import { ExternalLink, ArrowRight, Code2 } from 'lucide-react';

const featuredProject = {
  title: "CarDD AI Engine",
  description: "An end-to-end Machine Learning pipeline for automated vehicle damage assessment. Combines YOLOv8 for object detection, Segformer for precise pixel-level damage tracing, and a custom ResNet18 model for severity classification. Includes Grad-CAM explainability and a Flask web dashboard.",
  tags: ["PyTorch", "YOLOv8", "Transformers", "Flask", "OpenCV"],
  image: "https://images.unsplash.com/photo-1542362567-b07e54358753?auto=format&fit=crop&q=80&w=1000",
  github: "#",
  demo: "#"
};

const otherProjects = [
  {
    title: "NeuroGen AI Image Synthesizer",
    description: "A Generative Adversarial Network (GAN) built from scratch to synthesize high-resolution medical imagery for data augmentation.",
    tags: ["TensorFlow", "GANs", "Python"],
    github: "#"
  },
  {
    title: "CryptoArb Trading Bot",
    description: "High-frequency triangular arbitrage trading bot connecting to multiple CEX WebSockets using async Python.",
    tags: ["AsyncIO", "WebSockets", "Pandas"],
    github: "#"
  }
];

const Projects = () => {
  return (
    <section id="projects" className="py-24">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6 }}
      >
        <div className="flex flex-col items-center mb-16">
          <h2 className="text-3xl md:text-5xl font-bold tracking-tight mb-4">Featured Work</h2>
          <div className="w-24 h-1 bg-gradient-to-r from-primary to-accent rounded-full" />
        </div>

        {/* Featured Project */}
        <div className="glass-card overflow-hidden group mb-12">
          <div className="grid grid-cols-1 lg:grid-cols-2">
            <div className="relative h-64 lg:h-auto overflow-hidden">
              <div className="absolute inset-0 bg-primary/20 group-hover:bg-transparent transition-colors z-10" />
              <img 
                src={featuredProject.image} 
                alt={featuredProject.title} 
                className="object-cover w-full h-full transform group-hover:scale-105 transition-transform duration-700"
              />
            </div>
            <div className="p-8 md:p-12 flex flex-col justify-center">
              <span className="text-accent font-semibold tracking-wider uppercase text-sm mb-2">Featured Project</span>
              <h3 className="text-3xl font-bold text-white mb-4">{featuredProject.title}</h3>
              <p className="text-foreground/80 leading-relaxed mb-6">
                {featuredProject.description}
              </p>
              <div className="flex flex-wrap gap-2 mb-8">
                {featuredProject.tags.map(tag => (
                  <span key={tag} className="text-xs px-3 py-1 bg-white/5 border border-white/10 rounded-full text-foreground/90">
                    {tag}
                  </span>
                ))}
              </div>
              <div className="flex items-center gap-4">
                <a href={featuredProject.demo} className="flex items-center gap-2 px-6 py-3 bg-primary text-white rounded-full font-semibold hover:bg-primary/90 transition-colors">
                  <ExternalLink size={18} /> Live Demo
                </a>
                <a href={featuredProject.github} className="flex items-center gap-2 p-3 bg-white/5 border border-white/10 rounded-full hover:bg-white/10 transition-colors">
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"/><path d="M9 18c-4.51 2-5-2-7-2"/></svg>
                </a>
              </div>
            </div>
          </div>
        </div>

        {/* Other Projects Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {otherProjects.map((project, idx) => (
            <motion.div 
              key={project.title}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: idx * 0.1 }}
              className="glass-card p-8 flex flex-col h-full group hover:-translate-y-2 transition-transform duration-300"
            >
              <div className="flex justify-between items-start mb-6">
                <div className="p-3 bg-primary/10 text-primary rounded-lg">
                  <Code2 size={24} />
                </div>
                <a href={project.github} className="text-foreground/50 hover:text-white transition-colors">
                  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"/><path d="M9 18c-4.51 2-5-2-7-2"/></svg>
                </a>
              </div>
              <h3 className="text-xl font-bold text-white mb-3 group-hover:text-primary transition-colors">{project.title}</h3>
              <p className="text-foreground/70 text-sm leading-relaxed mb-6 flex-grow">
                {project.description}
              </p>
              <div className="flex flex-wrap gap-2 mt-auto">
                {project.tags.map(tag => (
                  <span key={tag} className="text-xs text-foreground/50">
                    #{tag}
                  </span>
                ))}
              </div>
            </motion.div>
          ))}
        </div>
        
        <div className="mt-12 text-center">
          <a href="#" className="inline-flex items-center gap-2 text-primary hover:text-accent font-semibold transition-colors">
            View all projects on GitHub <ArrowRight size={18} />
          </a>
        </div>
      </motion.div>
    </section>
  );
};

export default Projects;
