import React from 'react';
import { motion } from 'framer-motion';
import { Crosshair, PenTool, BarChart3 } from 'lucide-react';

const pipelineSteps = [
  {
    id: 1,
    title: "Stage 1: Object Detection",
    model: "YOLOv8s",
    description: "The raw image is passed through a custom-trained YOLOv8 architecture to instantly draw high-precision bounding boxes around 6 specific types of vehicle damage.",
    icon: Crosshair
  },
  {
    id: 2,
    title: "Stage 2: Semantic Segmentation",
    model: "Segformer-B0",
    description: "The cropped bounding boxes are fed into a Transformer-based segmentation network to trace the exact pixel-perfect physical boundaries of the damage.",
    icon: PenTool
  },
  {
    id: 3,
    title: "Stage 3: Severity Classification",
    model: "ResNet18 + GradCAM",
    description: "A ResNet classifier analyzes the damage and engineered metadata to predict severity (High, Medium, Low). Grad-CAM heatmaps are generated for explainable AI.",
    icon: BarChart3
  }
];

const Pipeline = () => {
  return (
    <section id="pipeline" className="py-24">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6 }}
      >
        <div className="flex flex-col items-center mb-16 text-center">
          <h2 className="text-3xl md:text-5xl font-bold tracking-tight mb-4">The AI Pipeline</h2>
          <div className="w-24 h-1 bg-gradient-to-r from-primary to-accent rounded-full mb-6" />
          <p className="text-foreground/70 max-w-2xl">Three separate neural networks working in harmony to orchestrate the perfect prediction.</p>
        </div>

        <div className="max-w-4xl mx-auto relative">
          {/* Vertical Line */}
          <div className="absolute left-[20px] md:left-1/2 top-0 bottom-0 w-[2px] bg-white/10 transform md:-translate-x-1/2" />
          
          <div className="flex flex-col gap-12">
            {pipelineSteps.map((step, idx) => {
              const isEven = idx % 2 === 0;
              const Icon = step.icon;
              return (
                <motion.div 
                  key={step.id}
                  initial={{ opacity: 0, x: isEven ? -50 : 50 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true, margin: "-100px" }}
                  transition={{ duration: 0.6 }}
                  className={`relative flex flex-col md:flex-row items-start ${isEven ? 'md:flex-row-reverse' : ''}`}
                >
                  {/* Timeline Node */}
                  <div className="absolute left-[20px] md:left-1/2 transform -translate-x-1/2 w-10 h-10 rounded-full bg-background border-4 border-primary flex items-center justify-center z-10">
                    <Icon className="w-4 h-4 text-primary" />
                  </div>
                  
                  {/* Content Card */}
                  <div className={`w-full md:w-[45%] pl-16 md:pl-0 ${isEven ? 'md:pr-16 text-left md:text-right' : 'md:pl-16 text-left'}`}>
                    <div className="glass-card p-6 hover:border-primary/30 transition-colors group">
                      <span className="text-sm font-semibold text-accent mb-2 block">{step.title}</span>
                      <h3 className="text-xl font-bold text-white mb-4 group-hover:text-primary transition-colors">{step.model}</h3>
                      <p className="text-foreground/80 text-sm leading-relaxed">
                        {step.description}
                      </p>
                    </div>
                  </div>
                </motion.div>
              )
            })}
          </div>
        </div>
      </motion.div>
    </section>
  );
};

export default Pipeline;
