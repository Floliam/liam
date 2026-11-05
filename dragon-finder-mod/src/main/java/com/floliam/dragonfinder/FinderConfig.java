package com.floliam.dragonfinder;

import net.minecraftforge.common.ForgeConfigSpec;

import java.util.List;

/** Einstellungen in config/dragonfinder-client.toml */
public final class FinderConfig {
    public static final ForgeConfigSpec SPEC;

    public static final ForgeConfigSpec.BooleanValue SHOW_HUD;
    public static final ForgeConfigSpec.BooleanValue CHAT_ALERTS;
    public static final ForgeConfigSpec.BooleanValue ALERT_SOUND;
    public static final ForgeConfigSpec.ConfigValue<List<? extends String>> DRAGON_ENTITIES;
    public static final ForgeConfigSpec.BooleanValue SCAN_LAIRS;
    public static final ForgeConfigSpec.ConfigValue<List<? extends String>> LAIR_BLOCKS;
    public static final ForgeConfigSpec.IntValue LAIR_MIN_BLOCKS;

    static {
        ForgeConfigSpec.Builder b = new ForgeConfigSpec.Builder();

        b.push("display");
        SHOW_HUD = b.comment("Anzeige oben links beim Spielstart einblenden (im Spiel mit Taste K umschaltbar)")
                .define("showHud", true);
        CHAT_ALERTS = b.comment("Im eigenen Chat melden, wenn ein Drache oder Drachenhort neu entdeckt wird")
                .define("chatAlerts", true);
        ALERT_SOUND = b.comment("Bei einer Meldung einen kurzen Ton abspielen (nur für dich hörbar)")
                .define("sound", true);
        b.pop();

        b.push("dragons");
        DRAGON_ENTITIES = b.comment("Entity-IDs, die als Drache zählen")
                .defineList("entities", List.of(
                        "iceandfire:fire_dragon",
                        "iceandfire:ice_dragon",
                        "iceandfire:lightning_dragon"), o -> o instanceof String);
        b.pop();

        b.push("lairs");
        SCAN_LAIRS = b.comment("Geladene Chunks nach Drachenhorten (Schatzhaufen) durchsuchen")
                .define("scan", true);
        LAIR_BLOCKS = b.comment("Block-IDs, an denen ein Hort erkannt wird")
                .defineList("blocks", List.of(
                        "iceandfire:gold_pile",
                        "iceandfire:silver_pile",
                        "iceandfire:copper_pile"), o -> o instanceof String);
        LAIR_MIN_BLOCKS = b.comment("So viele Schatzhaufen-Blöcke braucht es, bis eine Stelle als Hort gilt")
                .defineInRange("minBlocks", 8, 1, 1000);
        b.pop();

        SPEC = b.build();
    }

    private FinderConfig() {
    }
}
