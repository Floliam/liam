package com.floliam.locatorbar;

import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.fml.IExtensionPoint;
import net.minecraftforge.fml.ModLoadingContext;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.config.ModConfig;
import net.minecraftforge.network.NetworkConstants;

@Mod(PlayerLocatorBar.MOD_ID)
public class PlayerLocatorBar {
    public static final String MOD_ID = "playerlocatorbar";

    public PlayerLocatorBar() {
        ModLoadingContext context = ModLoadingContext.get();

        // Rein clientseitig: Server müssen die Mod nicht haben, und sie verlangt sie auch nicht.
        context.registerExtensionPoint(IExtensionPoint.DisplayTest.class,
                () -> new IExtensionPoint.DisplayTest(() -> NetworkConstants.IGNORESERVERONLY, (remote, isServer) -> true));

        // Client-Config liegt im eigenen config-Ordner -> gilt nur für dich, nicht für Welt oder Server.
        context.registerConfig(ModConfig.Type.CLIENT, LocatorConfig.SPEC);

        DistExecutor.unsafeRunWhenOn(Dist.CLIENT, () -> ClientSetup::init);
    }
}
