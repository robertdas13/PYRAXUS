import React from 'react';
import { aboutData } from '../mock';
import { MapPin, Mail, Award } from 'lucide-react';
import { Card } from './ui/card';

const About = () => {
  return (
    <section id="about" className="section-container">
      <div className="section-content">
        <div className="section-header">
          <h2 className="section-title">About Me</h2>
          <div className="title-underline"></div>
        </div>

        <div className="about-grid">
          <div className="about-image-wrapper">
            <div className="about-glow"></div>
            <img
              src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=500&h=500&fit=crop&crop=faces"
              alt={aboutData.name}
              className="about-image"
            />
          </div>

          <div className="about-content">
            <h3 className="about-name">{aboutData.name}</h3>
            <p className="about-title">{aboutData.title}</p>
            
            <p className="about-bio">{aboutData.bio}</p>

            <div className="about-details">
              <div className="detail-item">
                <MapPin size={20} className="detail-icon" />
                <span>{aboutData.location}</span>
              </div>
              <div className="detail-item">
                <Mail size={20} className="detail-icon" />
                <span>{aboutData.email}</span>
              </div>
            </div>

            <div className="stats-grid">
              <Card className="stat-card">
                <Award className="stat-icon" size={24} />
                <div className="stat-number">{aboutData.experience}</div>
                <div className="stat-label">Years Experience</div>
              </Card>
              <Card className="stat-card">
                <Award className="stat-icon" size={24} />
                <div className="stat-number">{aboutData.projects}</div>
                <div className="stat-label">Projects Done</div>
              </Card>
              <Card className="stat-card">
                <Award className="stat-icon" size={24} />
                <div className="stat-number">{aboutData.clients}</div>
                <div className="stat-label">Happy Clients</div>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default About;