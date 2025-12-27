"use client";

import { useMemo } from "react";

interface MarkdownProps {
  content: string;
  className?: string;
}

/**
 * Simple Markdown renderer for dark theme
 * Supports: headers, bold, italic, code, lists, tables, links
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

    // Code blocks (``` ... ```)
    html = html.replace(
      /```(\w*)\n([\s\S]*?)```/g,
      (_, lang, code) =>
        `<pre class="bg-zinc-900 border border-zinc-700 rounded-lg p-3 my-2 overflow-x-auto"><code class="text-sm text-zinc-300 font-mono">${code.trim()}</code></pre>`
    );

    // Inline code (`...`)
    html = html.replace(
      /`([^`]+)`/g,
      '<code class="bg-zinc-800 text-zinc-300 px-1.5 py-0.5 rounded text-sm font-mono">$1</code>'
    );

    // Headers
    html = html.replace(
      /^#### (.+)$/gm,
      '<h4 class="text-sm font-semibold text-foreground mt-4 mb-2">$1</h4>'
    );
    html = html.replace(
      /^### (.+)$/gm,
      '<h3 class="text-base font-semibold text-foreground mt-4 mb-2">$1</h3>'
    );
    html = html.replace(
      /^## (.+)$/gm,
      '<h2 class="text-lg font-semibold text-foreground mt-4 mb-2">$1</h2>'
    );
    html = html.replace(
      /^# (.+)$/gm,
      '<h1 class="text-xl font-bold text-foreground mt-4 mb-2">$1</h1>'
    );

    // Bold and Italic
    html = html.replace(
      /\*\*\*(.+?)\*\*\*/g,
      '<strong><em class="text-foreground">$1</em></strong>'
    );
    html = html.replace(
      /\*\*(.+?)\*\*/g,
      '<strong class="text-foreground font-semibold">$1</strong>'
    );
    html = html.replace(
      /\*(.+?)\*/g,
      '<em class="text-foreground italic">$1</em>'
    );
    html = html.replace(
      /_(.+?)_/g,
      '<em class="text-foreground italic">$1</em>'
    );

    // Links
    html = html.replace(
      /\[([^\]]+)\]\(([^)]+)\)/g,
      '<a href="$2" target="_blank" rel="noopener noreferrer" class="text-primary hover:underline">$1</a>'
    );

    // Horizontal rules
    html = html.replace(
      /^---$/gm,
      '<hr class="border-zinc-700 my-4" />'
    );

    // Unordered lists
    html = html.replace(/^[\s]*[-*+] (.+)$/gm, (match, item) => {
      return `<li class="text-foreground ml-4 list-disc">${item}</li>`;
    });

    // Ordered lists
    html = html.replace(/^[\s]*(\d+)\. (.+)$/gm, (match, num, item) => {
      return `<li class="text-foreground ml-4 list-decimal" value="${num}">${item}</li>`;
    });

    // Wrap consecutive list items in ul/ol
    html = html.replace(
      /(<li class="text-foreground ml-4 list-disc">[\s\S]*?<\/li>\n?)+/g,
      '<ul class="my-2 space-y-1">$&</ul>'
    );
    html = html.replace(
      /(<li class="text-foreground ml-4 list-decimal"[\s\S]*?<\/li>\n?)+/g,
      '<ol class="my-2 space-y-1">$&</ol>'
    );

    // Tables
    html = html.replace(
      /^\|(.+)\|$/gm,
      (match, content) => {
        const cells = content.split("|").map((cell: string) => cell.trim());

        // Check if this is a separator row
        if (cells.every((cell: string) => /^[-:]+$/.test(cell))) {
          return ""; // Skip separator rows
        }

        const cellHtml = cells
          .map((cell: string) => `<td class="border border-zinc-700 px-3 py-2 text-sm">${cell}</td>`)
          .join("");
        return `<tr class="border-b border-zinc-700">${cellHtml}</tr>`;
      }
    );

    // Wrap table rows
    html = html.replace(
      /(<tr[\s\S]*?<\/tr>\n?)+/g,
      '<div class="overflow-x-auto my-2"><table class="w-full border-collapse border border-zinc-700 text-sm"><tbody>$&</tbody></table></div>'
    );

    // Blockquotes
    html = html.replace(
      /^&gt; (.+)$/gm,
      '<blockquote class="border-l-4 border-zinc-600 pl-4 my-2 text-muted-foreground italic">$1</blockquote>'
    );

    // Paragraphs - wrap remaining text blocks
    html = html.replace(
      /^(?!<[a-z]|$)(.+)$/gm,
      '<p class="text-foreground my-1">$1</p>'
    );

    // Clean up empty paragraphs
    html = html.replace(/<p class="text-foreground my-1"><\/p>/g, "");

    // Add line breaks
    html = html.replace(/\n\n/g, '<br class="my-2" />');

    return html;
  }, [content]);

  if (!renderedContent) return null;

  return (
    <div
      className={`markdown-content ${className}`}
      dangerouslySetInnerHTML={{ __html: renderedContent }}
    />
  );
}
