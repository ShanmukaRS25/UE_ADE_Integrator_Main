using UnrealBuildTool;

public class UE_ADE_DemoServerTarget : TargetRules
{
	public UE_ADE_DemoServerTarget(TargetInfo Target) : base(Target)
	{
		DefaultBuildSettings = BuildSettingsVersion.Latest;
		IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
		Type = TargetType.Server;
		ExtraModuleNames.Add("UE_ADE_Demo");
	}
}
