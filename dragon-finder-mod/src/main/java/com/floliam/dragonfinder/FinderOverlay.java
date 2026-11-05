package com.floliam.dragonfinder;

import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.ChatFormatting;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiComponent;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraftforge.client.gui.ForgeIngameGui;
import net.minecraftforge.client.gui.IIngameOverlay;

/** Zwei Zeilen oben links: nächster Drache und nächster Hort mit Entfernung, Richtung und Höhe. */
public class FinderOverlay implements IIngameOverlay {
    private static final int BACKGROUND = 0x80000000;

    @Override
    public void render(ForgeIngameGui gui, PoseStack poseStack, float partialTick, int width, int height) {
        Minecraft mc = Minecraft.getInstance();
        LocalPlayer player = mc.player;
        if (player == null || mc.options.hideGui || mc.options.renderDebug || !ClientSetup.isVisible()) {
            return;
        }
        Font font = mc.font;
        double px = Mth.lerp(partialTick, player.xo, player.getX());
        double py = Mth.lerp(partialTick, player.yo, player.getY());
        double pz = Mth.lerp(partialTick, player.zo, player.getZ());
        float viewYaw = player.getViewYRot(partialTick);

        String dragonLine;
        int dragonColor;
        DragonTracker.Sighting sighting = DragonTracker.nearest;
        if (sighting != null && sighting.entity.isAlive()) {
            Entity e = sighting.entity;
            double dx = Mth.lerp(partialTick, e.xo, e.getX()) - px;
            double dy = Mth.lerp(partialTick, e.yo, e.getY()) - py;
            double dz = Mth.lerp(partialTick, e.zo, e.getZ()) - pz;
            dragonLine = DragonTracker.displayName(e, sighting.key) + "  " + describe(dx, dy, dz, viewYaw, e.getY());
            dragonColor = color(DragonTracker.style(sighting.key));
        } else {
            dragonLine = "Kein Drache in Sichtweite";
            dragonColor = 0xAAAAAA;
        }

        String lairLine = null;
        int lairColor = 0;
        LairScanner.Lair lair = LairScanner.nearest(player);
        if (lair != null) {
            lairLine = lair.title() + "  " + describe(lair.x - px, lair.y - py, lair.z - pz, viewYaw, lair.y);
            lairColor = color(lair.style());
        }

        int lines = lairLine == null ? 1 : 2;
        int boxWidth = Math.max(font.width(dragonLine), lairLine == null ? 0 : font.width(lairLine));
        GuiComponent.fill(poseStack, 2, 2, 6 + boxWidth, 4 + lines * 10, BACKGROUND);
        font.drawShadow(poseStack, dragonLine, 4, 4, dragonColor);
        if (lairLine != null) {
            font.drawShadow(poseStack, lairLine, 4, 14, lairColor);
        }
    }

    private static String describe(double dx, double dy, double dz, float viewYaw, double targetY) {
        long distance = Math.round(Math.sqrt(dx * dx + dy * dy + dz * dz));
        return distance + " m  " + Directions.arrow(dx, dz, viewYaw) + " " + Directions.compass(dx, dz)
                + "  Y " + Mth.floor(targetY) + " " + Directions.height(dy);
    }

    private static int color(ChatFormatting formatting) {
        Integer c = formatting.getColor();
        return c != null ? c : 0xFFFFFF;
    }
}
