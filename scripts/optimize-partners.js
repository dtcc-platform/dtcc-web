#!/usr/bin/env node

/**
 * Partner Logo Optimization Script
 *
 * This script optimizes partner logos by:
 * 1. Creating backups of original PNG files
 * 2. Converting to WebP format with 85% quality
 * 3. Resizing to max 800px width (logos don't need to be huge)
 * 4. Generating a report of size savings
 *
 * Usage: node scripts/optimize-partners.js
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
  maxWidth: 800, // Partner logos don't need to be huge
  webpQuality: 85,
  partnersDir: path.join(projectRoot, 'public', 'content', 'partners'),
  backupDir: path.join(projectRoot, 'public', 'content', 'partners', 'originals'),
};

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
 * Optimize a single partner logo
 */
async function optimizeLogo(pngPath) {
  const parsedPath = path.parse(pngPath);
  const webpPath = path.join(parsedPath.dir, `${parsedPath.name}.webp`);
  const fileName = path.basename(pngPath);

  try {
    // Check if original exists
    const originalSize = await getFileSize(pngPath);
    if (originalSize === 0) {
      console.log(`⚠️  Skipped: ${fileName} (file not found)`);
      return null;
    }

    // Create backup
    await fs.mkdir(CONFIG.backupDir, { recursive: true });
    const backupPath = path.join(CONFIG.backupDir, fileName);

    // Only backup if not already backed up
    const backupExists = await getFileSize(backupPath) > 0;
    if (!backupExists) {
      await fs.copyFile(pngPath, backupPath);
    }

    // Get image metadata
    const metadata = await sharp(pngPath).metadata();

    // Optimize and convert to WebP
    await sharp(pngPath)
      .resize(CONFIG.maxWidth, null, {
        withoutEnlargement: true,
        fit: 'inside',
      })
      .webp({ quality: CONFIG.webpQuality })
      .toFile(webpPath);

    const webpSize = await getFileSize(webpPath);
    const savings = originalSize - webpSize;
    const savingsPercent = ((savings / originalSize) * 100).toFixed(1);

    console.log(`✓ ${fileName}`);
    console.log(`  Original: ${formatBytes(originalSize)} (${metadata.width}x${metadata.height})`);
    console.log(`  WebP:     ${formatBytes(webpSize)}`);
    console.log(`  Saved:    ${formatBytes(savings)} (${savingsPercent}%)`);
    console.log('');

    return {
      fileName,
      originalSize,
      webpSize,
      savings,
      savingsPercent: parseFloat(savingsPercent),
    };
  } catch (err) {
    console.error(`✗ Failed to optimize ${fileName}:`);
    console.error(`  Error: ${err.message}`);
    console.log('');
    return null;
  }
}

/**
 * Main execution
 */
async function main() {
  console.log('🖼️  Partner Logo Optimization Script');
  console.log('====================================\n');

  // Check if partners directory exists
  try {
    await fs.access(CONFIG.partnersDir);
  } catch (err) {
    console.error(`Error: Partners directory not found at ${CONFIG.partnersDir}`);
    process.exit(1);
  }

  // Find all PNG files in partners directory
  const files = await fs.readdir(CONFIG.partnersDir);
  const pngFiles = files.filter(f => f.toLowerCase().endsWith('.png'));

  if (pngFiles.length === 0) {
    console.log('No PNG files found to optimize.');
    return;
  }

  console.log(`📁 Found ${pngFiles.length} PNG partner logos`);
  console.log(`📁 Backups will be saved to: ${CONFIG.backupDir}\n`);

  const results = [];

  // Process each PNG file
  for (const pngFile of pngFiles) {
    const fullPath = path.join(CONFIG.partnersDir, pngFile);
    const result = await optimizeLogo(fullPath);
    if (result) {
      results.push(result);
    }
  }

  // Generate summary report
  console.log('====================================');
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
  console.log('1. Update PartnersPage.vue to use WebP images');
  console.log('2. Test the partner logos display correctly');
  console.log('3. Consider removing original PNG files if WebP works well');
  console.log(`4. Originals are backed up in: ${CONFIG.backupDir}`);
}

// Run the script
main().catch((err) => {
  console.error('Fatal error:', err);
  process.exit(1);
});
