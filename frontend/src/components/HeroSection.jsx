import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowUpRight, X } from 'lucide-react';

const ACCENT_COLOR = '#5E0ED7';
const EASE_BEZIER = [0.22, 1, 0.36, 1];

const fadeDown = {
  initial: { opacity: 0, y: -20 },
  animate: (custom = 0) => ({
    opacity: 1,
    y: 0,
    transition: {
      delay: custom * 0.1,
      duration: 0.5,
      ease: EASE_BEZIER,
    },
  }),
};

const fadeUp = {
  initial: { opacity: 0, y: 32 },
  animate: (custom = 0) => ({
    opacity: 1,
    y: 0,
    transition: {
      delay: custom * 0.12,
      duration: 0.6,
      ease: EASE_BEZIER,
    },
  }),
};

export default function HeroSection({ onExploreClick }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navLinks = ['Story', 'Expertise', 'Studios', 'Feedback'];
  const headingWords = ['Fearless', 'Vision', 'Delivered'];

  const stats = [
    { number: '300', label: 'CRAFTED\nBRANDS' },
    { number: '200', label: 'DIGITAL\nPRODUCTS' },
    { number: '100', label: 'VENTURES\nFUNDED' },
  ];

  const handleNavClick = (_link) => {
    setMobileMenuOpen(false);
    if (onExploreClick) {
      onExploreClick();
    } else {
      const el = document.getElementById('valuation-workspace');
      el?.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <section className="relative min-h-screen w-full flex flex-col justify-between overflow-hidden font-['Inter',sans-serif]">
      {/* 1. Full-screen autoplaying background video */}
      <div className="absolute inset-0 w-full h-full -z-10 overflow-hidden bg-slate-900">
        <video
          autoPlay
          loop
          muted
          playsInline
          className="w-full h-full object-cover"
          src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260517_222138_3e3205be-3364-417b-a64a-bfe087acbec4.mp4"
        />
        {/* Subtle translucent overlay to enhance text readability while showcasing the video */}
        <div className="absolute inset-0 bg-white/20 backdrop-blur-[1px]" />
      </div>

      {/* 2. NAVIGATION BAR */}
      <nav className="w-full px-5 sm:px-8 md:px-12 pt-5 md:pt-6 flex items-center justify-between z-20">
        {/* Left: Logo */}
        <motion.div
          variants={fadeDown}
          initial="initial"
          animate="animate"
          custom={0}
          className="flex items-center gap-3 cursor-pointer"
          onClick={() => handleNavClick('Home')}
        >
          <div
            className="w-8 h-8 rounded-full border-2 flex items-center justify-center"
            style={{ borderColor: ACCENT_COLOR }}
          >
            <div
              className="w-2.5 h-2.5 rounded-full"
              style={{ backgroundColor: ACCENT_COLOR }}
            />
          </div>
        </motion.div>

        {/* Center: Desktop Nav Links */}
        <div className="hidden md:flex items-center gap-8 lg:gap-10">
          {navLinks.map((link, idx) => (
            <motion.button
              key={link}
              variants={fadeDown}
              initial="initial"
              animate="animate"
              custom={idx + 1}
              onClick={() => handleNavClick(link)}
              className="text-[14px] font-semibold tracking-widest uppercase text-black hover:opacity-75 transition-opacity cursor-pointer bg-transparent border-none"
            >
              {link}
            </motion.button>
          ))}
        </div>

        {/* Right: Hamburger button */}
        <motion.button
          variants={fadeDown}
          initial="initial"
          animate="animate"
          custom={5}
          onClick={() => setMobileMenuOpen(true)}
          aria-label="Open mobile menu"
          className="w-9 h-9 rounded-full bg-black flex flex-col items-center justify-center gap-1 cursor-pointer hover:bg-neutral-800 transition-colors"
        >
          <span className="w-4 h-0.5 bg-white rounded-full" />
          <span className="w-4 h-0.5 bg-white rounded-full" />
          <span className="w-4 h-0.5 bg-white rounded-full" />
        </motion.button>
      </nav>

      {/* Mobile Menu Overlay */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3, ease: EASE_BEZIER }}
            className="fixed inset-0 z-50 bg-white flex flex-col justify-between px-6 sm:px-8 py-6"
          >
            {/* Top row */}
            <div className="flex items-center justify-between">
              <div
                className="w-8 h-8 rounded-full border-2 flex items-center justify-center"
                style={{ borderColor: ACCENT_COLOR }}
              >
                <div
                  className="w-2.5 h-2.5 rounded-full"
                  style={{ backgroundColor: ACCENT_COLOR }}
                />
              </div>

              <button
                onClick={() => setMobileMenuOpen(false)}
                aria-label="Close mobile menu"
                className="w-9 h-9 rounded-full bg-black flex items-center justify-center text-white cursor-pointer hover:bg-neutral-800 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Nav list */}
            <div className="flex flex-col gap-8 mt-16">
              {navLinks.map((link) => (
                <button
                  key={link}
                  onClick={() => handleNavClick(link)}
                  className="text-left text-3xl font-semibold tracking-widest uppercase text-black hover:opacity-70 transition-opacity bg-transparent border-none cursor-pointer"
                >
                  {link}
                </button>
              ))}
            </div>

            {/* Bottom CTA */}
            <div className="mt-auto pt-8 border-t border-neutral-100">
              <button
                onClick={() => handleNavClick('Work With Us')}
                className="flex items-center gap-2 text-xl font-semibold tracking-widest uppercase cursor-pointer"
                style={{ color: ACCENT_COLOR }}
              >
                <span>Work With Us</span>
                <ArrowUpRight className="w-5 h-5" />
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 3. STATS ROW (middle section) */}
      <div className="flex-1 flex items-center justify-end px-5 sm:px-8 md:px-12 py-8 md:py-0 z-10">
        <div className="flex items-start gap-5 sm:gap-8 md:gap-10">
          {stats.map((stat, idx) => (
            <motion.div
              key={stat.label}
              variants={fadeUp}
              initial="initial"
              animate="animate"
              custom={idx + 2}
              className="text-right flex flex-col items-end"
            >
              <div
                className="font-semibold text-black tracking-wide flex items-baseline leading-none"
                style={{ fontSize: 'clamp(1.5rem, 5vw, 3.5rem)' }}
              >
                <span
                  className="mr-0.5"
                  style={{ color: ACCENT_COLOR, fontSize: '0.5em', verticalAlign: 'super' }}
                >
                  +
                </span>
                <span>{stat.number}</span>
              </div>
              <div className="text-[10px] sm:text-xs md:text-sm font-semibold tracking-widest uppercase text-black whitespace-pre-line leading-tight mt-1.5 sm:mt-2">
                {stat.label}
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* 4. BOTTOM SECTION */}
      <div className="w-full px-5 sm:px-8 md:px-12 pb-8 md:pb-12 flex flex-col gap-6 md:gap-12 z-10">
        {/* Row A: Tagline + CTA */}
        <div className="flex items-center justify-between gap-4">
          <motion.p
            variants={fadeUp}
            initial="initial"
            animate="animate"
            custom={5}
            className="text-[10px] sm:text-xs md:text-sm font-semibold tracking-widest uppercase text-black max-w-[130px] sm:max-w-[160px] md:max-w-xs leading-normal"
          >
            Shaping Bold <br /> Visions Into Power <br /> For Your Tribe
          </motion.p>

          <motion.button
            variants={fadeUp}
            initial="initial"
            animate="animate"
            custom={6}
            onClick={() => handleNavClick('Work With Us')}
            className="flex items-center gap-1.5 sm:gap-2 text-base sm:text-xl md:text-2xl font-semibold tracking-widest uppercase whitespace-nowrap cursor-pointer hover:opacity-80 transition-opacity bg-transparent border-none"
            style={{ color: ACCENT_COLOR }}
          >
            <span>Work With Us</span>
            <ArrowUpRight className="w-[18px] h-[18px] sm:w-[22px] sm:h-[22px]" />
          </motion.button>
        </div>

        {/* Row B: Description + Main Heading */}
        <div className="flex items-end justify-between gap-3 sm:gap-4">
          {/* Left: Fixed-width description */}
          <motion.div
            variants={fadeUp}
            initial="initial"
            animate="animate"
            custom={7}
            className="w-[120px] sm:w-[180px] md:w-[280px] shrink-0"
          >
            <p className="text-[9px] sm:text-xs md:text-sm font-semibold tracking-widest uppercase text-black text-left md:text-right leading-relaxed">
              Creative Studios Built Around Elevating Your Vision Into Striking Reality
            </p>
          </motion.div>

          {/* Right: Main Heading stacked */}
          <div className="flex flex-col items-end text-right">
            {headingWords.map((word, wordIdx) => (
              <div key={word} className="overflow-hidden">
                <motion.div
                  initial={{ y: '110%' }}
                  animate={{ y: 0 }}
                  transition={{
                    delay: 0.4 + wordIdx * 0.14,
                    duration: 0.7,
                    ease: EASE_BEZIER,
                  }}
                  className="font-semibold uppercase text-black"
                  style={{
                    fontSize: 'clamp(2rem, 9vw, 9rem)',
                    lineHeight: 0.88,
                  }}
                >
                  {word}
                </motion.div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
