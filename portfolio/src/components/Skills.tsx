import React from 'react';
import { motion } from 'framer-motion';
import { Terminal, Brain, Layout, Database } from 'lucide-react';

const skillCategories = [
  {
    title: "AI / Machine Learning",
    icon: Brain,
    skills: ["PyTorch", "TensorFlow", "YOLOv8", "Transformers", "Computer Vision", "Scikit-Learn"]
  },
  {
    title: "Web Development",
    icon: Layout,
    skills: ["React", "TypeScript", "Tailwind CSS", "Next.js", "Flask", "Node.js"]
  },
  {
    title: "Programming",
    icon: Terminal,
    skills: ["Python", "JavaScript/TypeScript", "C++", "SQL", "Bash", "Go"]
  },
  {
    title: "Databases & Tools",
    icon: Database,
    skills: ["PostgreSQL", "MongoDB", "Docker", "Git", "AWS", "Linux"]
  }
];

const Skills = () => {
  return (
    <section id="skills" className="py-24">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6 }}
      >
        <div className="flex flex-col items-center mb-16">
          <h2 className="text-3xl md:text-5xl font-bold tracking-tight mb-4">Technical Arsenal</h2>
          <div className="w-24 h-1 bg-gradient-to-r from-primary to-accent rounded-full" />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {skillCategories.map((category, idx) => {
            const Icon = category.icon;
            return (
              <motion.div 
                key={category.title}
                initial={{ opacity: 0, scale: 0.95 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: idx * 0.1 }}
                className="glass-card p-8 group hover:border-primary/40 transition-colors"
              >
                <div className="flex items-center gap-4 mb-6">
                  <div className="p-3 bg-white/5 rounded-lg border border-white/10 group-hover:border-primary/50 transition-colors">
                    <Icon className="text-primary w-6 h-6" />
                  </div>
                  <h3 className="text-xl font-bold">{category.title}</h3>
                </div>
                
                <div className="flex flex-wrap gap-3">
                  {category.skills.map((skill) => (
                    <span 
                      key={skill} 
                      className="px-4 py-2 text-sm bg-white/5 border border-white/10 rounded-full text-foreground/80 hover:text-white hover:border-primary/50 transition-colors cursor-default"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </motion.div>
            )
          })}
        </div>
      </motion.div>
    </section>
  );
};

export default Skills;
