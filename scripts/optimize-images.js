#!/usr/bin/env node

/**
 * Image Optimization Script
 *
 * This script optimizes large images in the public directory by:
 * 1. Creating backups of original files
 * 2. Converting to WebP format with 85% quality
 * 3. Resizing to max 1920px width (maintaining aspect ratio)
 * 4. Generating a report of size savings
 *
 * Usage: node scripts/optimize-images.js
 */

import sharp from 'sharp';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

// Get __dirname equivalent in ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuration
const projectRoot = path.resolve(__dirname, '..');
const CONFIG = {
  maxWidth: 1920,
  webpQuality: 85,
  publicDir: path.join(projectRoot, 'public'),
  backupDir: path.join(projectRoot, 'public', 'originals'),
};

// List of images to optimize (identified from audit)
const IMAGES_TO_OPTIMIZE = [
  'content/Tara-Wood-BW.jpg',
  'content/News Placeholder.png',
  'content/Projects Placeholder.png',
  'content/chalmers.png',
  'content/gibraltargatan.png',
  'content/lindholmen.png',
];

/**
 * Format bytes to human-readable size
 */
function formatBytes(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Get file size
 */
async function getFileSize(filePath) {
  try {
    const stats = await fs.stat(filePath);
    return stats.size;
  } catch (err) {
    return 0;
  }
}

/**
 * Create backup directory structure
 */
async function ensureBackupDir(originalPath) {
  const relativePath = path.relative(CONFIG.publicDir, path.dirname(originalPath));
  const backupPath = path.join(CONFIG.backupDir, relativePath);
  await fs.mkdir(backupPath, { recursive: true });
  return backupPath;
}

/**
 * Optimize a single image
 */
async function optimizeImage(imagePath) {
  const fullPath = path.join(CONFIG.publicDir, imagePath);
  const parsedPath = path.parse(fullPath);
  const webpPath = path.join(parsedPath.dir, `${parsedPath.name}.webp`);

  try {
    // Check if original exists
    const originalSize = await getFileSize(fullPath);
    if (originalSize === 0) {
      console.log(`⚠️  Skipped: ${imagePath} (file not found)`);
      return null;
    }

    // Create backup
    const backupDir = await ensureBackupDir(fullPath);
    const backupPath = path.join(backupDir, path.basename(fullPath));

    // Only backup if not already backed up
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

/**
 * Main execution
 */
async function main() {
  console.log('🖼️  Image Optimization Script');
  console.log('================================\n');

  // Ensure backup directory exists
  await fs.mkdir(CONFIG.backupDir, { recursive: true });
  console.log(`📁 Backups will be saved to: ${CONFIG.backupDir}\n`);

  const results = [];

  // Process each image
  for (const imagePath of IMAGES_TO_OPTIMIZE) {
    const result = await optimizeImage(imagePath);
    if (result) {
      results.push(result);
    }
  }

  // Generate summary report
  console.log('================================');
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
  console.log('📝 Next steps:');
  console.log('1. Test the WebP images in your application');
  console.log('2. Update Vue components to use WebP with PNG fallback');
  console.log('3. Consider removing original PNG files if WebP works well');
  console.log(`4. Originals are backed up in: ${CONFIG.backupDir}`);
}

// Run the script
main().catch((err) => {
  console.error('Fatal error:', err);
  process.exit(1);
});
