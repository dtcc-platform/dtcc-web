#!/usr/bin/env node

/**
 * Optimize Remaining Images Script
 *
 * Optimizes remaining large PNG images:
 * - TC-illustration med ringar.png
 * - News content images
 *
 * Usage: node scripts/optimize-remaining.js
 */

import sharp from 'sharp';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, '..');

const CONFIG = {
  maxWidth: 1920,
  webpQuality: 85,
  publicDir: path.join(projectRoot, 'public'),
};

// Images to optimize
const IMAGES_TO_OPTIMIZE = [
  'content/TC-illustration med ringar.png',
  'content/news/test19.png',
  'content/news/test193.png',
  'content/news/multi-images-news-item.png',
  'content/news/new-tests-for-nadia.png',
  'content/news/new-tests-for-nadia-1.png',
];

function formatBytes(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

async function getFileSize(filePath) {
  try {
    const stats = await fs.stat(filePath);
    return stats.size;
  } catch (err) {
    return 0;
  }
}

async function ensureBackupDir(originalPath) {
  const relativePath = path.relative(CONFIG.publicDir, path.dirname(originalPath));
  const backupPath = path.join(CONFIG.publicDir, 'originals', relativePath);
  await fs.mkdir(backupPath, { recursive: true });
  return backupPath;
}

async function optimizeImage(imagePath) {
  const fullPath = path.join(CONFIG.publicDir, imagePath);
  const parsedPath = path.parse(fullPath);
  const webpPath = path.join(parsedPath.dir, `${parsedPath.name}.webp`);

  try {
    const originalSize = await getFileSize(fullPath);
    if (originalSize === 0) {
      console.log(`⚠️  Skipped: ${imagePath} (file not found)`);
      return null;
    }

    // Create backup
    const backupDir = await ensureBackupDir(fullPath);
    const backupPath = path.join(backupDir, path.basename(fullPath));

    const backupExists = await getFileSize(backupPath) > 0;
    if (!backupExists) {
      await fs.copyFile(fullPath, backupPath);
    }

    // Get image metadata
    const metadata = await sharp(fullPath).metadata();

    // Optimize and convert to WebP
    await sharp(fullPath)
      .resize(CONFIG.maxWidth, null, {
        withoutEnlargement: true,
        fit: 'inside',
      })
      .webp({ quality: CONFIG.webpQuality })
      .toFile(webpPath);

    const webpSize = await getFileSize(webpPath);
    const savings = originalSize - webpSize;
    const savingsPercent = ((savings / originalSize) * 100).toFixed(1);

    console.log(`✓ ${imagePath}`);
    console.log(`  Original: ${formatBytes(originalSize)} (${metadata.width}x${metadata.height})`);
    console.log(`  WebP:     ${formatBytes(webpSize)}`);
    console.log(`  Saved:    ${formatBytes(savings)} (${savingsPercent}%)`);
    console.log('');

    return {
      path: imagePath,
      originalSize,
      webpSize,
      savings,
      savingsPercent: parseFloat(savingsPercent),
    };
  } catch (err) {
    console.error(`✗ Failed to optimize ${imagePath}:`);
    console.error(`  Error: ${err.message}`);
    console.log('');
    return null;
  }
}

async function main() {
  console.log('🖼️  Remaining Images Optimization Script');
  console.log('=========================================\n');

  const results = [];

  for (const imagePath of IMAGES_TO_OPTIMIZE) {
    const result = await optimizeImage(imagePath);
    if (result) {
      results.push(result);
    }
  }

  console.log('=========================================');
  console.log('📊 Summary Report\n');

  if (results.length === 0) {
    console.log('No images were optimized.');
    return;
  }

  const totalOriginal = results.reduce((sum, r) => sum + r.originalSize, 0);
  const totalWebp = results.reduce((sum, r) => sum + r.webpSize, 0);
  const totalSavings = totalOriginal - totalWebp;
  const totalSavingsPercent = ((totalSavings / totalOriginal) * 100).toFixed(1);

  console.log(`Images optimized:  ${results.length}`);
  console.log(`Original size:     ${formatBytes(totalOriginal)}`);
  console.log(`Optimized size:    ${formatBytes(totalWebp)}`);
  console.log(`Total savings:     ${formatBytes(totalSavings)} (${totalSavingsPercent}%)`);
  console.log('');
  console.log('✅ Optimization complete!');
  console.log('');
  console.log('📝 Next step: Update Vue components to use WebP images');
}

main().catch((err) => {
  console.error('Fatal error:', err);
  process.exit(1);
});
