import React from 'react';
import { skills } from '../mock';
import { Card } from './ui/card';

const Skills = () => {
  return (
    <section id="skills" className="section-container section-dark">
      <div className="section-content">
        <div className="section-header">
          <h2 className="section-title">Skills & Expertise</h2>
          <div className="title-underline"></div>
          <p className="section-description">
            Technologies and tools I use to bring ideas to life
          </p>
        </div>

        <div className="skills-grid">
          {skills.map((skill, index) => (
            <Card key={index} className="skill-card">
              <div className="skill-header">
                <h3 className="skill-name">{skill.name}</h3>
                <span className="skill-percentage">{skill.level}%</span>
              </div>
              <div className="skill-bar-container">
                <div
                  className="skill-bar"
                  style={{
                    width: `${skill.level}%`,
                    animation: `fillBar 1.5s ease-out ${index * 0.1}s forwards`
                  }}
                ></div>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Skills;