<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="1.7.0-Wroclaw" minimumScale="0" maximumScale="1e+08" hasScaleBasedVisibilityFlag="0">
  <transparencyLevelInt>255</transparencyLevelInt>
  <renderer-v2 attr="sesso" symbollevels="0" type="categorizedSymbol">
    <categories>
      <category symbol="0" value="Femmina" label="Femmina"/>
      <category symbol="1" value="Indeterminato" label="Indeterminato"/>
      <category symbol="2" value="Maschio" label="Maschio"/>
    </categories>
    <symbols>
      <symbol outputUnit="MM" alpha="1" type="marker" name="0">
        <layer pass="0" class="SimpleMarker" locked="0">
          <prop k="angle" v="0"/>
          <prop k="color" v="255,85,127,255"/>
          <prop k="color_border" v="255,85,127,255"/>
          <prop k="name" v="arrow"/>
          <prop k="offset" v="0,0.5"/>
          <prop k="size" v="3"/>
        </layer>
        <layer pass="0" class="SimpleMarker" locked="0">
          <prop k="angle" v="0"/>
          <prop k="color" v="255,85,127,255"/>
          <prop k="color_border" v="255,85,127,255"/>
          <prop k="name" v="circle"/>
          <prop k="offset" v="0,-1"/>
          <prop k="size" v="2"/>
        </layer>
        <layer pass="0" class="SimpleMarker" locked="0">
          <prop k="angle" v="0"/>
          <prop k="color" v="255,255,255,255"/>
          <prop k="color_border" v="255,255,255,255"/>
          <prop k="name" v="circle"/>
          <prop k="offset" v="0,-1"/>
          <prop k="size" v="1"/>
        </layer>
        <layer pass="0" class="SimpleMarker" locked="0">
          <prop k="angle" v="90"/>
          <prop k="color" v="255,0,0,255"/>
          <prop k="color_border" v="255,85,127,255"/>
          <prop k="name" v="line"/>
          <prop k="offset" v="1,0"/>
          <prop k="size" v="3"/>
        </layer>
      </symbol>
      <symbol outputUnit="MM" alpha="1" type="marker" name="1">
        <layer pass="0" class="SimpleMarker" locked="0">
          <prop k="angle" v="0"/>
          <prop k="color" v="255,255,255,255"/>
          <prop k="color_border" v="0,0,0,255"/>
          <prop k="name" v="circle"/>
          <prop k="offset" v="0,0"/>
          <prop k="size" v="2"/>
        </layer>
      </symbol>
      <symbol outputUnit="MM" alpha="1" type="marker" name="2">
        <layer pass="0" class="SimpleMarker" locked="0">
          <prop k="angle" v="0"/>
          <prop k="color" v="0,0,255,255"/>
          <prop k="color_border" v="0,0,255,255"/>
          <prop k="name" v="circle"/>
          <prop k="offset" v="0,0"/>
          <prop k="size" v="2"/>
        </layer>
        <layer pass="0" class="SimpleMarker" locked="0">
          <prop k="angle" v="25"/>
          <prop k="color" v="0,0,255,255"/>
          <prop k="color_border" v="0,0,255,255"/>
          <prop k="name" v="arrow"/>
          <prop k="offset" v="0.4,-1.5"/>
          <prop k="size" v="2"/>
        </layer>
        <layer pass="0" class="SimpleMarker" locked="0">
          <prop k="angle" v="0"/>
          <prop k="color" v="255,255,255,255"/>
          <prop k="color_border" v="0,0,0,255"/>
          <prop k="name" v="circle"/>
          <prop k="offset" v="0,0"/>
          <prop k="size" v="1.5"/>
        </layer>
      </symbol>
    </symbols>
    <source-symbol>
      <symbol outputUnit="MM" alpha="1" type="marker" name="0">
        <layer pass="0" class="SimpleMarker" locked="0">
          <prop k="angle" v="0"/>
          <prop k="color" v="52,0,129,255"/>
          <prop k="color_border" v="0,0,0,255"/>
          <prop k="name" v="circle"/>
          <prop k="offset" v="0,0"/>
          <prop k="size" v="2"/>
        </layer>
      </symbol>
    </source-symbol>
    <colorramp type="gradient" name="[source]">
      <prop k="color1" v="0,0,255,255"/>
      <prop k="color2" v="207,205,255,255"/>
    </colorramp>
    <rotation field=""/>
    <sizescale field=""/>
  </renderer-v2>
  <customproperties/>
  <displayfield>gid</displayfield>
  <label>0</label>
  <labelattributes>
    <label fieldname="" text="Etichetta"/>
    <family fieldname="" name="MS Shell Dlg 2"/>
    <size fieldname="" units="pt" value="12"/>
    <bold fieldname="" on="0"/>
    <italic fieldname="" on="0"/>
    <underline fieldname="" on="0"/>
    <strikeout fieldname="" on="0"/>
    <color fieldname="" red="0" blue="0" green="0"/>
    <x fieldname=""/>
    <y fieldname=""/>
    <offset x="0" y="0" units="pt" yfieldname="" xfieldname=""/>
    <angle fieldname="" value="0" auto="0"/>
    <alignment fieldname="" value="center"/>
    <buffercolor fieldname="" red="255" blue="255" green="255"/>
    <buffersize fieldname="" units="pt" value="1"/>
    <bufferenabled fieldname="" on=""/>
    <multilineenabled fieldname="" on=""/>
    <selectedonly on=""/>
  </labelattributes>
  <edittypes>
    <edittype type="0" name="area"/>
    <edittype type="0" name="classi_eta"/>
    <edittype type="0" name="data_schedatura"/>
    <edittype type="0" name="eta_max"/>
    <edittype type="0" name="eta_min"/>
    <edittype type="0" name="gid"/>
    <edittype type="0" name="id_individuo"/>
    <edittype type="0" name="id_scheda_ind"/>
    <edittype type="0" name="note"/>
    <edittype type="0" name="nr_individuo"/>
    <edittype type="0" name="osservazioni"/>
    <edittype type="0" name="scavo"/>
    <edittype type="0" name="schedatore"/>
    <edittype type="0" name="sesso"/>
    <edittype type="0" name="sito"/>
    <edittype type="0" name="us"/>
  </edittypes>
  <editform></editform>
  <editforminit></editforminit>
  <annotationform></annotationform>
  <attributeactions/>
  <overlay display="false" type="diagram">
    <renderer item_interpretation="linear">
      <diagramitem size="0" value="0"/>
      <diagramitem size="0" value="0"/>
    </renderer>
    <factory sizeUnits="MM" type="Pie">
      <wellknownname>Pie</wellknownname>
      <classificationfield>0</classificationfield>
    </factory>
    <scalingAttribute>0</scalingAttribute>
  </overlay>
</qgis>
