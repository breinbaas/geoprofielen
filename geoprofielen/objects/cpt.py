__author__ = "Breinbaas | Rob van Putten"
__copyright__ = "Copyright 2020"
__credits__ = ["Rob van Putten"]
__license__ = "GPL"
__version__ = "0.1.0"
__maintainer__ = "Rob van Putten"
__email__ = "breinbaasnl@gmail.com"
__status__ = "Development"

from pydantic import BaseModel
from typing import List
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as patches
from matplotlib.ticker import MultipleLocator
import math

from enum import IntEnum

from .soillayer import SoilLayer
from ..settings import HDSR_SOIL_COLORS, DEFAULT_MINIMUM_LAYERHEIGHT

class ConversionType(IntEnum):
    THREE_TYPE_RULE = 0
    SBT_DUTCH_NON_NORMALIZED = 1
    SBT_DUTCH_NORMALIZED = 2
    NEN_5104 = 3

RF_MAX = 10.
QC_MAX = 50.

GEF_COLUMN_Z = 1
GEF_COLUMN_QC = 2
GEF_COLUMN_FS = 3
GEF_COLUMN_U = 6
GEF_COLUMN_Z_CORRECTED = 11

NEN5140 = [
    ['veen',8.1], # immediate translation to HDSR soils
        ['veen',5],
        ['klei_humeus',4],
        ['klei_humeus',3.3],
        ['klei_siltig',2.9],
        ['klei_siltig',2.5],
        ['klei_siltig',2.2],
        ['klei_zandig',1.8],
        ['zand',1.4],
        ['zand',1.1],
        ['zand',0.8],
        ['zand',0.6],
        ['zand',0.0]
    ]

class CPT(BaseModel):
    x: float = 0.0
    y: float = 0.0
    z_top: float = 0.0

    z: List[float] = []
    qc: List[float] = []
    fs: List[float] = []
    u: List[float] = []
    Rf: List[float] = []

    name: str = ""
    
    filedate: str = ""
    startdate: str = ""

    soillayers: List[SoilLayer] = []
    filename: str = ""

    @classmethod
    def from_file(self, filename: str) -> 'CPT':
        cpt = CPT()
        cpt.read(filename)
        return cpt

    @property
    def date(self) -> str:
        """Return the date of the CPT in the following order (if available) startdate, filedata, empty string (no date)

        Args:
            None

        Returns:
            str: date in format YYYYMMDD"""
        if self.startdate != "":
            return self.startdate
        elif self.filedate != "":
            return self.filedate
        else:
            raise ValueError("This geffile has no date or invalid date information.")

    @property
    def z_min(self) -> float:
        """
        Return the lowest point of the CPT

        Args:
            None

        Returns:
            float: deepest point in CPT
        """
        return self.z[-1]

    @property 
    def has_u(self) -> bool:
        """
        Does this CPT has waterpressure

        Args:
            None

        Return:
            bool: true is CPT has waterpressure readings, false otherwise
        """
        return max(self.u) > 0 or min(self.u) < 0

    def read_from_gef_stringlist(self, lines: List[str]) -> None:
        """
        Read a GEF from the indivual lines

        Args:
            lines (List[str]): list of strings

        Returns:
            None
        """
        reading_header = True
        metadata = {
            "record_seperator":"",
            "column_seperator":" ",
            "columnvoids":{}, 
            "columninfo":{}
        }
        for line in lines:
            if reading_header:
                if line.find("#EOH") >= 0:
                    reading_header = False
                else:
                    self._parse_header_line(line, metadata)
            else:
                self._parse_data_line(line, metadata)

        self._calculate()

    def read(self, filename: str) -> None:
        self.filename = filename
        extension = Path(filename).suffix.lower()
        if extension == ".gef":
            self._read_gef(filename)
        else:
            raise NotImplementedError(f"Unknown and unhandled file extension {extension}")
    
    def _read_gef(self, filename: str) -> None:
        """
        Read a GEF file

        Args:
            filename (str): the name of the file to be read

        Returns:
            None
        """
        lines = open(filename, "r", encoding="utf-8", errors="ignore").readlines()

        self.read_from_gef_stringlist(lines)

    def _calculate(self) -> None:
        """
        Calculate other parameters from the qc and fs values

        Args:
            None

        Returns:
            None"""
        for qc, fs in zip(self.qc, self.fs):
            if qc == 0.0:
                self.Rf.append(RF_MAX)
            else:
                self.Rf.append(fs / qc * 100.)

    def _parse_header_line(self, line: str, metadata: dict) -> None:
        try:
            args = line.split("=")
            keyword, argline = args[0], args[1]
        except Exception as e:
            raise ValueError(f"Error reading headerline '{line}' -> error {e}")

        keyword = keyword.strip().replace("#", "")
        argline = argline.strip()
        args = argline.split(",")

        if keyword == "RECORDSEPARATOR":
            metadata["record_seperator"] = args[0]
        elif keyword == "COLUMNSEPARATOR":
            metadata["column_seperator"] = args[0]
        elif keyword == "COLUMNINFO":
            try:
                column = int(args[0])
                dtype = int(args[3].strip())
                if dtype == GEF_COLUMN_Z_CORRECTED:
                    dtype = GEF_COLUMN_Z # use corrected depth instead of depth                
                metadata["columninfo"][dtype] = column - 1
            except Exception as e:
                raise ValueError(f"Error reading columninfo '{line}' -> error {e}")
        elif keyword == "XYID":
            try:
                self.x = round(float(args[1].strip()), 2)
                self.y = round(float(args[2].strip()), 2)
            except:
                raise ValueError(f"Error reading xyid '{line}' -> error {e}")
        elif keyword == "ZID":
            try:
                self.z_top = float(args[1].strip())
            except:
                raise ValueError(f"Error reading zid '{line}' -> error {e}")     
        elif keyword == "COLUMNVOID":
            try:
                col = int(args[0].strip())
                metadata["columnvoids"][col - 1] = float(args[1].strip())
            except Exception as e:
                raise ValueError(f"Error reading columnvoid '{line}' -> error {e}")  
        elif keyword == "TESTID":
            self.name = args[0].strip()    
        elif keyword == "FILEDATE":
            try:
                yyyy = int(args[0].strip())
                mm = int(args[1].strip())
                dd = int(args[2].strip())   

                if yyyy < 1900 or yyyy > 2100 or mm < 1 or mm > 12 or dd < 1 or dd > 31:
                    raise ValueError(f"Invalid date {yyyy}-{mm}-{dd}")            

                self.filedate = f"{yyyy}{mm:02}{dd:02}"
            except:                
                self.filedate = ""
        elif keyword == "STARTDATE":
            try:
                yyyy = int(args[0].strip())
                mm = int(args[1].strip())
                dd = int(args[2].strip())
                self.startdate = f"{yyyy}{mm:02}{dd:02}"
                if yyyy < 1900 or yyyy > 2100 or mm < 1 or mm > 12 or dd < 1 or dd > 31:
                    raise ValueError(f"Invalid date {yyyy}-{mm}-{dd}")
            except:                
                self.startdate = ""
        
    def _parse_data_line(self, line: str, metadata: dict) -> None:
        try:
            if len(line.strip())==0: return
            args = line.replace(metadata["record_seperator"], '').strip().split(metadata["column_seperator"])
            args = [float(arg.strip()) for arg in args if len(arg.strip()) > 0 and arg.strip() != metadata["record_seperator"]]
            
            # skip lines that have a columnvoid
            for col_index, voidvalue in metadata["columnvoids"].items():
                if args[col_index] == voidvalue:
                    return  

            zcolumn = metadata["columninfo"][GEF_COLUMN_Z]
            qccolumn = metadata["columninfo"][GEF_COLUMN_QC]
            fscolumn = metadata["columninfo"][GEF_COLUMN_FS]

            ucolumn = -1
            if GEF_COLUMN_U in metadata["columninfo"].keys():
                ucolumn = metadata["columninfo"][GEF_COLUMN_U]

            dz = self.z_top - abs(args[zcolumn])            
            self.z.append(dz)

            qc = args[qccolumn]
            if qc <= 0:
                qc = 1e-3
            self.qc.append(qc)
            fs = args[fscolumn]
            if fs <= 0:
                fs = 1e-6
            self.fs.append(fs)

            if ucolumn > -1:
                self.u.append(args[ucolumn])
            else:
                self.u.append(0.0)

        except Exception as e:
            raise ValueError(f"Error reading dataline '{line}' -> error {e}") 

    def as_numpy(self) -> np.array:
        """
        Return the CPT data as a numpy array with;
        
        col     value
        0       z
        1       qc
        2       fs
        3       Rf
        4       u

        Args:
            None

        Returns:
            np.array: the CPT data as a numpy array"""
        return np.transpose(np.array([self.z, self.qc, self.fs, self.Rf, self.u]))
    
    def as_dataframe(self) -> pd.DataFrame:
        """
        Return the CPT data as a dataframe with columns;        
        z, qc, fs, Rf, u

        Args:
            None

        Returns:
            pd.DataFrame: the CPT data as a DataFrame"""
        data = self.as_numpy()
        return pd.DataFrame(data=data, columns=["z", "qc", "fs", "Rf", "u"])
    
    def plot(self, size_x: float = 10, size_y: float = 12, filepath: str ="", filename: str="") -> None:
        """Plot the CPT

        Args:
            size_x (float): figure width in inches, default 8
            size_y (float): figure height in inches, default 12
            filepath (str): the path to save the file to (filename will be automatic), default "" (no save)

        Returns:
            None
        """
        data = self.as_dataframe()
        fig = plt.figure(figsize=(size_x, size_y))
        
        spec = gridspec.GridSpec(ncols=4, nrows=1, width_ratios=[3, 1, 1, 1])

        z1 = round(self.z_min) - 1.0
        z2 = round(self.z_top) + 1.0
        
        ax_qc = fig.add_subplot(spec[0,0])
        data.plot(x='qc',y='z', ax=ax_qc, sharey=True, label='qc [MPa]')
        ax_qc.grid(which="both")
        ax_qc.set_xlim(0,QC_MAX)
        plt.title(self.name)

        for soillayer in self.soillayers:
            facecolor = HDSR_SOIL_COLORS[soillayer.soilcode]
            ax_qc.add_patch(
                patches.Rectangle(
                    (40, soillayer.z_bottom),
                    10,
                    soillayer.height,
                    fill=True,
                    facecolor=facecolor,
                )
            )

        ax_fs = fig.add_subplot(spec[0,1])
        data.plot(x='fs',y='z', ax=ax_fs, sharey=True, label='fs [MPa]')
        ax_fs.grid(which="both")
        ax_fs.set_xlim(0,0.2)

        ax_Rf = fig.add_subplot(spec[0,2])
        data.plot(x='Rf',y='z', ax=ax_Rf, sharey=True, label='Rf [%]')
        ax_Rf.grid(which="both")
        ax_Rf.set_xlim(0,10.)

        if self.has_u:
            ax_u = fig.add_subplot(spec[0,3])
            data.plot(x='u',y='z', ax=ax_u, sharey=True, label='u [kPa]')
            ax_u.grid(which="both") 
        
        plt.tight_layout()
        
        
        if len(filepath) > 0:
            if len(filename)==0:
                filename = f"{self.name}.png"
            path = Path(filepath) / filename
            plt.savefig(path)

        plt.close()

    def filter(self, minimum_layer_height: float = DEFAULT_MINIMUM_LAYERHEIGHT) -> np.array:
        """Return the CPT data as a numpy array with;
        
        col     value
        0       ztop
        1       zbot
        2       qc
        3       fs
        4       Rf
        5       u

        Args:
            None

        Returns:
            np.array: the CPT data as a numpy array"""
        a = self.as_numpy()
        ls = np.arange(self.z[0], self.z[-1] - DEFAULT_MINIMUM_LAYERHEIGHT, -minimum_layer_height)
        
        result = []
        for i in range(1, len(ls)):
            ztop = ls[i-1]    
            zbot = ls[i]
            selection = a[(a[:,0] <= ztop) & (a[:,0] >= zbot)]
            layer = np.array([ztop, zbot])
            mean = np.mean(selection[:,1:], axis=0)
            result.append(np.concatenate((layer, mean), axis=None))

        return np.array(result)

    def _merge_layers(self) -> None:
        """Merge consecutive layers if they have the same soil code
        
        Args:
            None

        Returns:
            None
        """
        # merge layers with same name
        result = []
        for i in range(len(self.soillayers)):
            if i==0:
                result.append(self.soillayers[i])
            else:
                if self.soillayers[i].soilcode == result[-1].soilcode:
                    result[-1].z_bottom = self.soillayers[i].z_bottom
                else:
                    result.append(self.soillayers[i])
        self.soillayers = result

    def _convert_nen_5014(self, minimum_layer_height: float) -> List[SoilLayer]:
        """
        Conversion function for the rule as found in CUR162 electric cone

        Args:
            None

        Returns:
            List[SoilLayer]: the list of soillayers
        """
        self.soillayers = []             
        cptdata = self.filter(minimum_layer_height)
        for row in cptdata:
            Rf = row[4]
            for soilcode, _Rf in NEN5140:
                if Rf >= _Rf:
                    self.soillayers.append(SoilLayer(z_top=round(row[0],2), z_bottom=round(row[1],2), soilcode=soilcode))
                    break

        self._merge_layers()
    
    def _convert_three_type_rule(self, minimum_layer_height: float) -> List[SoilLayer]:
        """
        Conversion function for the three type rule

        Args:
            None

        Returns:
            List[SoilLayer]: the list of soillayers
        """
        #     0     1     2       3       4      5
        # get ztop, zbot, qc_avg, fs_avg, Rf_avg u_avg matrix   
        self.soillayers = []             
        cptdata = self.filter(minimum_layer_height)
        for row in cptdata:
            x = row[4]
            y = math.log(row[2])
            
            if x<0: x=0
            if x>10: x=10
            if y<-1: y=-1
            if y>2: y=2

            soilcode = ""
            if y <= x * 0.4 - 2:
                if x < 4:                    
                    soilcode = "klei_siltig" # eigenlijk gewoon klei maar dat is geen optie in de HDSR verzameling dus maar de slapste klei
                else:
                    soilcode = "veen"
            elif y > x * 0.4 - 0.30103:
                soilcode = "zand"
            else:
                soilcode = "klei_siltig" # idem vorige opmerking

            self.soillayers.append(SoilLayer(z_top=round(row[0],2), z_bottom=round(row[1],2), soilcode=soilcode))

        self._merge_layers()

    def _convert_sbt(self, minimum_layer_height: float) -> List[SoilLayer]:
        return []

    def _convert_sbtn(self, minimum_layer_height: float) -> List[SoilLayer]:
        return []
    
    def convert(self, conversion_type: ConversionType = ConversionType.THREE_TYPE_RULE, minimum_layer_height: float=DEFAULT_MINIMUM_LAYERHEIGHT) -> List[SoilLayer]:
        """
        Args:
            conversion_type (): type of conversion to apply, defaults to three type rule
            minimum_layer_height (float): minimum layerheight for the soillayers

        Returns:
            List[SoilLayer]: list of soillayers
        """
        if conversion_type == ConversionType.THREE_TYPE_RULE:
            self._convert_three_type_rule(minimum_layer_height=minimum_layer_height)
        elif conversion_type == ConversionType.NEN_5104:
            self._convert_nen_5014(minimum_layer_height=minimum_layer_height)
        else:
            raise NotImplementedError("The given conversion method has not been implemented yet.")




        
