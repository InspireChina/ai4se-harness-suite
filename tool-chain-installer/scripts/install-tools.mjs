#!/usr/bin/env node
// 安装 MCP 工具链到指定项目。
//
// 用法：
//   node install-tools.mjs <目标项目目录> [选项]
//
//   --tools <a,b,c>     安装指定工具（逗号分隔）
//   --group <name>      安装某一组（browser / context / data / observability）
//   --all               安装全部
//   --dry-run           只打印将要发生的改动
//   --format <fmt>      写入格式：both(默认) | mcp-json | opencode
//   --list              列出所有可用工具并退出

import fs from "node:fs"
import path from "node:path"
import { fileURLToPath } from "node:url"

const HERE = path.dirname(fileURLToPath(import.meta.url))
const CATALOG_PATH = path.join(HERE, "..", "catalog", "mcp-catalog.json")

// ── 参数解析 ────────────────────────────────────────────────────────
const args = process.argv.slice(2)
const opts = { tools: [], groups: [], all: false, dryRun: false, format: "both", list: false }
let target = null

for (let i = 0; i < args.length; i++) {
  const a = args[i]
  switch (a) {
    case "--tools": opts.tools = (args[++i] || "").split(",").map(s => s.trim()).filter(Boolean); break
    case "--group": opts.groups.push(args[++i]); break
    case "--all": opts.all = true; break
    case "--dry-run": opts.dryRun = true; break
    case "--format": opts.format = args[++i] || "both"; break
    case "--list": opts.list = true; break
    case "-h": case "--help": printUsage(0); break
    default:
      if (a.startsWith("-")) { console.error(`未知参数: ${a}`); printUsage(1) }
      target = a
  }
}

function printUsage(code) {
  console.log(fs.readFileSync(fileURLToPath(import.meta.url), "utf8").split("\n").slice(1, 11).map(l => l.replace(/^#\s?/, "")).join("\n"))
  process.exit(code)
}

// ── 目录 ────────────────────────────────────────────────────────────
const catalog = JSON.parse(fs.readFileSync(CATALOG_PATH, "utf8"))

if (opts.list) {
  for (const [group, items] of Object.entries(catalog)) {
    console.log(`\n${group}`)
    for (const t of items) {
      console.log(`  ${t.name.padEnd(20)} ${t.description}`)
      console.log(`  ${"".padEnd(20)} → ${t.command} ${t.args.join(" ")}`)
    }
  }
  console.log("")
  process.exit(0)
}

if (!target) {
  console.error("错误：缺少目标项目目录。")
  printUsage(1)
}
if (!fs.existsSync(target)) {
  console.error(`错误：目标目录不存在: ${target}`)
  process.exit(1)
}

const PROJECT_ROOT = fs.realpathSync(target)

// ── 选择工具 ────────────────────────────────────────────────────────
const selected = []
if (opts.all) {
  for (const items of Object.values(catalog)) selected.push(...items)
}
for (const g of opts.groups) {
  const items = catalog[g]
  if (!items) {
    console.error(`错误：未知分组 "${g}"。可用分组：${Object.keys(catalog).join(", ")}`)
    process.exit(1)
  }
  selected.push(...items)
}
if (opts.tools.length) {
  const all = Object.values(catalog).flat()
  for (const name of opts.tools) {
    const found = all.find(t => t.name === name)
    if (!found) {
      console.error(`错误：未知工具 "${name}"。用 --list 查看全部。`)
      process.exit(1)
    }
    selected.push(found)
  }
}
if (!selected.length) {
  console.error("错误：没有指定要安装的工具。用 --tools / --group / --all 指定。")
  printUsage(1)
}

// 去重
const unique = [...new Map(selected.map(t => [t.name, t])).values()]

// ── JSONC 容忍解析 / 写回 ──────────────────────────────────────────
function stripJsonComments(text) {
  let out = ""
  let inString = false
  let inLine = false
  let inBlock = false
  for (let i = 0; i < text.length; i++) {
    const c = text[i]
    const n = text[i + 1]
    if (inLine) {
      if (c === "\n") { inLine = false; out += c }
      continue
    }
    if (inBlock) {
      if (c === "*" && n === "/") { inBlock = false; i++ }
      continue
    }
    if (inString) {
      out += c
      if (c === "\\") { out += n ?? ""; i++; continue }
      if (c === '"') inString = false
      continue
    }
    if (c === '"') { inString = true; out += c; continue }
    if (c === "/" && n === "/") { inLine = true; i++; continue }
    if (c === "/" && n === "*") { inBlock = true; i++; continue }
    out += c
  }
  return out
}

function readJsonc(file) {
  if (!fs.existsSync(file)) return null
  const raw = fs.readFileSync(file, "utf8")
  try {
    return JSON.parse(stripJsonComments(raw))
  } catch (e) {
    console.error(`错误：无法解析 ${file} —— ${e.message}`)
    process.exit(1)
  }
}

function writeJson(file, data) {
  fs.writeFileSync(file, JSON.stringify(data, null, 2) + "\n", "utf8")
}

// ── 安装 ────────────────────────────────────────────────────────────
console.log("MCP 工具链安装器")
console.log(`  目标项目 : ${PROJECT_ROOT}`)
console.log(`  写入格式 : ${opts.format}`)
console.log(`  待安装   : ${unique.map(t => t.name).join(", ")}`)
console.log("")

const writeMcpJson = opts.format === "both" || opts.format === "mcp-json"
const writeOpencode = opts.format === "both" || opts.format === "opencode"

const mcpJsonPath = path.join(PROJECT_ROOT, ".mcp.json")
const opencodePath = path.join(PROJECT_ROOT, "opencode.jsonc")

if (writeMcpJson) {
  const existing = readJsonc(mcpJsonPath) || {}
  if (!existing.mcpServers) existing.mcpServers = {}
  for (const t of unique) {
    existing.mcpServers[t.name] = {
      command: t.command,
      args: t.args,
      ...(t.env && Object.keys(t.env).length ? { env: t.env } : {})
    }
  }
  if (opts.dryRun) {
    console.log(`  [计划] 写入 ${mcpJsonPath}`)
  } else {
    writeJson(mcpJsonPath, existing)
    console.log(`  [写入] ${mcpJsonPath}`)
  }
}

if (writeOpencode) {
  const existing = readJsonc(opencodePath) || { $schema: "https://opencode.ai/config.json" }
  if (!existing.$schema) existing.$schema = "https://opencode.ai/config.json"
  if (!existing.mcp) existing.mcp = {}
  for (const t of unique) {
    existing.mcp[t.name] = {
      type: "local",
      command: [t.command, ...t.args],
      enabled: true,
      ...(t.env && Object.keys(t.env).length ? { environment: t.env } : {})
    }
  }
  if (opts.dryRun) {
    console.log(`  [计划] 写入 ${opencodePath}`)
  } else {
    writeJson(opencodePath, existing)
    console.log(`  [写入] ${opencodePath}`)
  }
}

// ── 报告 ────────────────────────────────────────────────────────────
console.log("")
console.log("已配置的工具：")
for (const t of unique) {
  const used = t.usedBy?.length ? `（供 ${t.usedBy.join(", ")} 使用）` : ""
  console.log(`  - ${t.name.padEnd(20)} ${t.description} ${used}`)
}

const needsEnv = unique.filter(t => t.env && Object.keys(t.env).length)
if (needsEnv.length) {
  console.log("")
  console.log("需要配置环境变量（不要把密钥写进仓库）：")
  for (const t of needsEnv) {
    for (const [k] of Object.entries(t.env)) {
      console.log(`  - ${k}  (${t.name})`)
    }
  }
}

console.log("")
console.log("提示：修改 MCP 配置后需重启 opencode 才会生效。")
