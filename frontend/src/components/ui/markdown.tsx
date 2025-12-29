"use client";

import { useMemo } from "react";

interface MarkdownProps {
  content: string;
  className?: string;
}

/**
 * Enhanced Markdown renderer for dark theme with clean typography
 * Supports: headers, bold, italic, code, lists, tables, links, blockquotes
 */
export function Markdown({ content, className = "" }: MarkdownProps) {
  const renderedContent = useMemo(() => {
    if (!content) return null;

    // Process the markdown content
    let html = content;

    // Escape HTML to prevent XSS
    html = html
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");

    // Code blocks (``` ... ```) - must be processed first
    html = html.replace(
      /```(\w*)\n([\s\S]*?)```/g,
      (_, lang, code) =>
        `<pre class="md-code-block"><code class="md-code">${code.trim()}</code></pre>`
    );

    // Inline code (`...`)
    html = html.replace(
      /`([^`]+)`/g,
      '<code class="md-inline-code">$1</code>'
    );

    // Headers - process from h4 to h1 to avoid conflicts
    html = html.replace(/^#### (.+)$/gm, '<h4 class="md-h4">$1</h4>');
    html = html.replace(/^### (.+)$/gm, '<h3 class="md-h3">$1</h3>');
    html = html.replace(/^## (.+)$/gm, '<h2 class="md-h2">$1</h2>');
    html = html.replace(/^# (.+)$/gm, '<h1 class="md-h1">$1</h1>');

    // Bold and Italic - process combined first
    html = html.replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>');
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong class="md-bold">$1</strong>');
    html = html.replace(/(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)/g, '<em class="md-italic">$1</em>');
    html = html.replace(/(?<!_)_(?!_)(.+?)(?<!_)_(?!_)/g, '<em class="md-italic">$1</em>');

    // Links
    html = html.replace(
      /\[([^\]]+)\]\(([^)]+)\)/g,
      '<a href="$2" target="_blank" rel="noopener noreferrer" class="md-link">$1</a>'
    );

    // Horizontal rules
    html = html.replace(/^---$/gm, '<hr class="md-hr" />');

    // Blockquotes - process before paragraphs
    html = html.replace(
      /^&gt; (.+)$/gm,
      '<blockquote class="md-blockquote">$1</blockquote>'
    );

    // Unordered lists - mark for grouping
    html = html.replace(/^[\s]*[-*+] (.+)$/gm, '<li class="md-ul-item">$1</li>');

    // Ordered lists - mark for grouping
    html = html.replace(/^[\s]*(\d+)\. (.+)$/gm, '<li class="md-ol-item" value="$1">$2</li>');

    // Wrap consecutive unordered list items
    html = html.replace(
      /(<li class="md-ul-item">[\s\S]*?<\/li>\n?)+/g,
      '<ul class="md-ul">$&</ul>'
    );

    // Wrap consecutive ordered list items
    html = html.replace(
      /(<li class="md-ol-item"[\s\S]*?<\/li>\n?)+/g,
      '<ol class="md-ol">$&</ol>'
    );

    // Tables
    html = html.replace(
      /^\|(.+)\|$/gm,
      (match, tableContent) => {
        const cells = tableContent.split("|").map((cell: string) => cell.trim());

        // Skip separator rows
        if (cells.every((cell: string) => /^[-:]+$/.test(cell))) {
          return "";
        }

        const cellHtml = cells
          .map((cell: string) => `<td class="md-td">${cell}</td>`)
          .join("");
        return `<tr class="md-tr">${cellHtml}</tr>`;
      }
    );

    // Wrap table rows
    html = html.replace(
      /(<tr class="md-tr">[\s\S]*?<\/tr>\n?)+/g,
      '<div class="md-table-wrapper"><table class="md-table"><tbody>$&</tbody></table></div>'
    );

    // Process paragraphs - wrap text that isn't already in an element
    // Split by double newlines for paragraph breaks
    const blocks = html.split(/\n\n+/);
    html = blocks.map(block => {
      const trimmed = block.trim();
      // Don't wrap if already an HTML element or empty
      if (!trimmed || /^<[a-z]/.test(trimmed)) {
        return trimmed;
      }
      // Handle single newlines within a paragraph
      const processed = trimmed.replace(/\n/g, '<br />');
      return `<p class="md-p">${processed}</p>`;
    }).join('\n');

    // Clean up any remaining single newlines between block elements
    html = html.replace(/>\n</g, '><');

    return html;
  }, [content]);

  if (!renderedContent) return null;

  return (
    <div
      className={`markdown-content leading-relaxed ${className}`}
      dangerouslySetInnerHTML={{ __html: renderedContent }}
    />
  );
}
