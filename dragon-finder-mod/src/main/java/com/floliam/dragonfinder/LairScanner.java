package com.floliam.dragonfinder;

import net.minecraft.ChatFormatting;
import net.minecraft.client.Minecraft;
import net.minecraft.network.chat.TextComponent;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.chunk.LevelChunk;
import net.minecraft.world.level.chunk.LevelChunkSection;
import net.minecraftforge.registries.ForgeRegistries;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * Durchsucht die Chunks, die der Client geladen hat, nach Schatzhaufen (Gold, Silber, Kupfer).
 * Ice and Fire legt diese in Drachenhöhlen und -nestern an. So findet man Horte auch dann,
 * wenn der Drache selbst zu weit weg ist, um übertragen zu werden.
 */
final class LairScanner {
    private static final int CHUNKS_PER_TICK = 4;
    /** Treffer näher als das werden zu einem Hort zusammengefasst. */
    private static final double MERGE_DISTANCE = 40;

    static final List<Lair> LAIRS = new ArrayList<>();

    private static final ArrayDeque<ChunkPos> QUEUE = new ArrayDeque<>();
    private static final Set<Long> SCANNED = new HashSet<>();
    private static Map<Block, String> lairBlocks = Map.of();
    private static List<? extends String> lairBlocksSource;

    private LairScanner() {
    }

    static void queue(ChunkPos pos) {
        QUEUE.add(pos);
    }

    /** Neue Welt/Dimension: gefundene Horte vergessen. Die Warteschlange bleibt, sie gehört schon zur neuen Welt. */
    static void reset() {
        SCANNED.clear();
        LAIRS.clear();
    }

    static void process(Minecraft mc) {
        if (!FinderConfig.SCAN_LAIRS.get()) {
            QUEUE.clear();
            return;
        }
        Map<Block, String> kinds = lairBlocks();
        if (kinds.isEmpty()) {
            QUEUE.clear(); // Ice and Fire nicht installiert
            return;
        }
        for (int i = 0; i < CHUNKS_PER_TICK && !QUEUE.isEmpty(); i++) {
            ChunkPos pos = QUEUE.poll();
            if (SCANNED.contains(pos.toLong())) {
                continue;
            }
            LevelChunk chunk = mc.level.getChunkSource().getChunk(pos.x, pos.z, false);
            if (chunk == null) {
                continue;
            }
            SCANNED.add(pos.toLong());
            scan(mc, chunk, kinds);
        }
    }

    private static void scan(Minecraft mc, LevelChunk chunk, Map<Block, String> kinds) {
        Map<String, double[]> found = new HashMap<>(); // Art -> {Anzahl, Summe x, Summe y, Summe z}
        int baseX = chunk.getPos().getMinBlockX();
        int baseZ = chunk.getPos().getMinBlockZ();
        for (LevelChunkSection section : chunk.getSections()) {
            if (section == null || section.hasOnlyAir() || !section.maybeHas(s -> kinds.containsKey(s.getBlock()))) {
                continue;
            }
            int baseY = section.bottomBlockY();
            for (int y = 0; y < 16; y++) {
                for (int z = 0; z < 16; z++) {
                    for (int x = 0; x < 16; x++) {
                        String kind = kinds.get(section.getBlockState(x, y, z).getBlock());
                        if (kind != null) {
                            double[] f = found.computeIfAbsent(kind, k -> new double[4]);
                            f[0]++;
                            f[1] += baseX + x + 0.5;
                            f[2] += baseY + y;
                            f[3] += baseZ + z + 0.5;
                        }
                    }
                }
            }
        }
        found.forEach((kind, f) -> addHit(mc, kind, (int) f[0], f[1] / f[0], f[2] / f[0], f[3] / f[0]));
    }

    private static void addHit(Minecraft mc, String kind, int count, double x, double y, double z) {
        Lair lair = null;
        for (Lair l : LAIRS) {
            if (l.kind.equals(kind) && Math.hypot(l.x - x, l.z - z) < MERGE_DISTANCE) {
                lair = l;
                break;
            }
        }
        if (lair == null) {
            lair = new Lair(kind);
            LAIRS.add(lair);
        }
        int total = lair.count + count;
        lair.x = (lair.x * lair.count + x * count) / total;
        lair.y = (lair.y * lair.count + y * count) / total;
        lair.z = (lair.z * lair.count + z * count) / total;
        lair.count = total;

        if (!lair.announced && lair.count >= FinderConfig.LAIR_MIN_BLOCKS.get()) {
            lair.announced = true;
            announce(mc, lair);
        }
    }

    private static void announce(Minecraft mc, Lair lair) {
        if (!FinderConfig.CHAT_ALERTS.get() || mc.player == null) {
            return;
        }
        double dx = lair.x - mc.player.getX();
        double dz = lair.z - mc.player.getZ();
        String text = " entdeckt: " + Math.round(Math.sqrt(dx * dx + dz * dz)) + " m Richtung "
                + Directions.compass(dx, dz) + ", Y " + Mth.floor(lair.y);
        mc.player.displayClientMessage(new TextComponent("[Drachenfinder] ").withStyle(ChatFormatting.GOLD)
                .append(new TextComponent(lair.title()).withStyle(lair.style()))
                .append(new TextComponent(text).withStyle(ChatFormatting.GRAY)), false);
        DragonTracker.playSound(mc);
    }

    static Lair nearest(Player player) {
        int min = FinderConfig.LAIR_MIN_BLOCKS.get();
        Lair best = null;
        double bestDist = Double.MAX_VALUE;
        for (Lair l : LAIRS) {
            if (l.count < min) {
                continue;
            }
            double d = player.distanceToSqr(l.x, l.y, l.z);
            if (d < bestDist) {
                bestDist = d;
                best = l;
            }
        }
        return best;
    }

    private static Map<Block, String> lairBlocks() {
        List<? extends String> configured = FinderConfig.LAIR_BLOCKS.get();
        if (configured != lairBlocksSource) {
            Map<Block, String> map = new HashMap<>();
            for (String id : configured) {
                ResourceLocation rl = ResourceLocation.tryParse(id);
                Block block = rl == null ? null : ForgeRegistries.BLOCKS.getValue(rl);
                if (block != null && block != Blocks.AIR) {
                    map.put(block, rl.getPath());
                }
            }
            lairBlocks = map;
            lairBlocksSource = configured;
        }
        return lairBlocks;
    }

    static final class Lair {
        final String kind;
        double x;
        double y;
        double z;
        int count;
        boolean announced;

        Lair(String kind) {
            this.kind = kind;
        }

        String title() {
            return switch (kind) {
                case "gold_pile" -> "Goldhort (Feuerdrache)";
                case "silver_pile" -> "Silberhort (Eisdrache)";
                case "copper_pile" -> "Kupferhort (Blitzdrache)";
                default -> "Hort (" + kind + ")";
            };
        }

        ChatFormatting style() {
            return switch (kind) {
                case "gold_pile" -> ChatFormatting.YELLOW;
                case "silver_pile" -> ChatFormatting.WHITE;
                case "copper_pile" -> ChatFormatting.GOLD;
                default -> ChatFormatting.GRAY;
            };
        }
    }
}
