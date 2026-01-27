"use client";
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { BookOpen, History, Info, Home } from 'lucide-react';
import styles from './Navbar.module.css';

export default function Navbar() {
  const pathname = usePathname();
  const isActive = (path: string) => pathname === path ? styles.active : '';

  return (
    <nav className={styles.nav}>
      <div className={`container ${styles.navContainer}`}>
        <Link href="/" className={styles.logo}>
          <BookOpen color="var(--primary)" />
          Texo
        </Link>
        <div className={styles.menu}>
          <Link href="/" className={`${styles.navLink} ${isActive('/')}`}>
            <Home size={18} /> Create
          </Link>
          <Link href="/history" className={`${styles.navLink} ${isActive('/history')}`}>
            <History size={18} /> History
          </Link>
          <Link href="/about" className={`${styles.navLink} ${isActive('/about')}`}>
            <Info size={18} /> About
          </Link>
        </div>
      </div>
    </nav>
  );
}