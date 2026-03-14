import React, { useState } from 'react';
import { projects } from '../mock';
import { Card } from './ui/card';
import { ExternalLink } from 'lucide-react';
import { Button } from './ui/button';

const Projects = () => {
  const [hoveredProject, setHoveredProject] = useState(null);

  return (
    <section id="projects" className="section-container">
      <div className="section-content">
        <div className="section-header">
          <h2 className="section-title">Featured Projects</h2>
          <div className="title-underline"></div>
          <p className="section-description">
            A showcase of my recent work and creative explorations
          </p>
        </div>

        <div className="projects-grid">
          {projects.map((project) => (
            <Card
              key={project.id}
              className="project-card"
              onMouseEnter={() => setHoveredProject(project.id)}
              onMouseLeave={() => setHoveredProject(null)}
            >
              <div className="project-image-wrapper">
                <img
                  src={project.image}
                  alt={project.title}
                  className="project-image"
                />
                <div className={`project-overlay ${hoveredProject === project.id ? 'active' : ''}`}>
                  <Button className="project-view-btn">
                    <ExternalLink size={18} />
                  </Button>
                </div>
              </div>
              <div className="project-content">
                <h3 className="project-title">{project.title}</h3>
                <p className="project-description">{project.description}</p>
                <div className="project-tech">
                  {project.tech.map((tech, index) => (
                    <span key={index} className="tech-tag">
                      {tech}
                    </span>
                  ))}
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Projects;