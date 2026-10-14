import React from 'react';
import { motion } from 'framer-motion';
import { Briefcase } from 'lucide-react';

const experiences = [
  {
    id: 1,
    role: "AI Research Assistant",
    company: "University of Science and Technology",
    duration: "2024 - Present",
    description: "Conducted research in Computer Vision and Deep Learning. Developed novel architectures for automated damage assessment pipelines.",
    tags: ["PyTorch", "OpenCV", "Python", "ResNet"]
  },
  {
    id: 2,
    role: "Full-Stack Developer Intern",
    company: "TechNova Solutions",
    duration: "Summer 2023",
    description: "Built scalable web applications for enterprise clients. Integrated third-party APIs and optimized database queries.",
    tags: ["React", "Node.js", "PostgreSQL", "Docker"]
  }
];

const Experience = () => {
  return (
    <section id="experience" className="py-24">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6 }}
      >
        <div className="flex flex-col items-center mb-16">
          <h2 className="text-3xl md:text-5xl font-bold tracking-tight mb-4">Experience</h2>
          <div className="w-24 h-1 bg-gradient-to-r from-primary to-accent rounded-full" />
        </div>

        <div className="max-w-4xl mx-auto relative">
          {/* Vertical Line */}
          <div className="absolute left-[20px] md:left-1/2 top-0 bottom-0 w-[2px] bg-white/10 transform md:-translate-x-1/2" />
          
          <div className="flex flex-col gap-12">
            {experiences.map((exp, idx) => {
              const isEven = idx % 2 === 0;
              return (
                <motion.div 
                  key={exp.id}
                  initial={{ opacity: 0, x: isEven ? -50 : 50 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true, margin: "-100px" }}
                  transition={{ duration: 0.6 }}
                  className={`relative flex flex-col md:flex-row items-start ${isEven ? 'md:flex-row-reverse' : ''}`}
                >
                  {/* Timeline Node */}
                  <div className="absolute left-[20px] md:left-1/2 transform -translate-x-1/2 w-10 h-10 rounded-full bg-background border-4 border-primary flex items-center justify-center z-10">
                    <Briefcase className="w-4 h-4 text-primary" />
                  </div>
                  
                  {/* Content Card */}
                  <div className={`w-full md:w-[45%] pl-16 md:pl-0 ${isEven ? 'md:pr-16 text-left md:text-right' : 'md:pl-16 text-left'}`}>
                    <div className="glass-card p-6 hover:border-primary/30 transition-colors">
                      <span className="text-sm font-semibold text-accent mb-2 block">{exp.duration}</span>
                      <h3 className="text-xl font-bold text-white">{exp.role}</h3>
                      <h4 className="text-lg text-foreground/70 mb-4">{exp.company}</h4>
                      <p className="text-foreground/80 text-sm leading-relaxed mb-4">
                        {exp.description}
                      </p>
                      <div className={`flex flex-wrap gap-2 ${isEven ? 'md:justify-end' : ''}`}>
                        {exp.tags.map(tag => (
                          <span key={tag} className="text-xs px-2 py-1 bg-white/5 border border-white/10 rounded text-foreground/90">
                            {tag}
                          </span>
                        ))}
                      </div>
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

export default Experience;
